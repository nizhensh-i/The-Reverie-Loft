import json
import logging
import re
import secrets
from typing import Dict, Optional

from ..infrastructure.database.sqlalchemy import db
from ..models import ThirdPartyAccount, User
from .common.unit_of_work import SqlAlchemyUnitOfWork


class OAuthAccountService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    @staticmethod
    def safe_profile(raw_profile) -> Optional[Dict]:
        if raw_profile is None:
            return None
        try:
            return json.loads(json.dumps(raw_profile, default=str))
        except Exception as exc:  # noqa: BLE001
            logging.warning("原始第三方资料序列化失败: %s", exc)
            return None

    def extract_auth_user_profile(self, auth_user) -> Dict:
        return {
            "uuid": getattr(auth_user, "uuid", None),
            "username": getattr(auth_user, "username", None),
            "nickname": getattr(auth_user, "nickname", None),
            "avatar": getattr(auth_user, "avatar", None),
            "email": getattr(auth_user, "email", None),
            "mobile": getattr(auth_user, "mobile", None),
            "gender": auth_user.gender.value
            if getattr(auth_user, "gender", None)
            else None,
            "location": getattr(auth_user, "location", None),
            "company": getattr(auth_user, "company", None),
            "blog": getattr(auth_user, "blog", None),
            "remark": getattr(auth_user, "remark", None),
            "raw_user_info": self.safe_profile(
                getattr(auth_user, "raw_user_info", None)
            ),
        }

    def generate_username(self, base_name: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_]+", "", base_name or "").lower() or "user"
        candidate = slug
        index = 1
        while User.query.filter_by(username=candidate).first():
            candidate = f"{slug}{index}"
            index += 1
        return candidate

    @staticmethod
    def update_account_snapshot(account: ThirdPartyAccount, profile: Dict) -> None:
        account.nickname = profile["nickname"]
        account.avatar = profile["avatar"]
        account.email = profile["email"]
        account.mobile = profile["mobile"]
        account.gender = profile["gender"]
        account.location = profile["location"]
        account.company = profile["company"]
        account.blog = profile["blog"]
        account.remark = profile["remark"]
        account.raw_user_info = profile["raw_user_info"]

    def get_or_create_user(self, provider: str, auth_user) -> User:
        profile = self.extract_auth_user_profile(auth_user)
        uuid = profile.get("uuid")
        if not uuid:
            raise ValueError("第三方登录缺少 uuid")

        account = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid=uuid
        ).one_or_none()

        if account:
            self.update_account_snapshot(account, profile)
            self.session.add(account)
            user = User.query.get(account.user_id)
            if user and (not user.image and profile["avatar"]):
                user.image = profile["avatar"]
                self.session.add(user)
            return user

        username = self.generate_username(profile["username"])
        user = User(
            username=username,
            nickname=profile["nickname"],
            image=profile["avatar"],
            password=secrets.token_urlsafe(32),
            has_password=False,
        )
        self.session.add(user)
        self.session.flush()

        account = ThirdPartyAccount(
            provider=provider,
            user_id=user.id,
            **profile,
        )
        self.session.add(account)
        return user

    def bind_third_party_account(
        self, provider: str, auth_user, user: User
    ) -> ThirdPartyAccount:
        profile = self.extract_auth_user_profile(auth_user)
        uuid = profile.get("uuid")
        if not uuid:
            raise ValueError("第三方登录缺少 uuid")

        existing_account = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid=uuid
        ).one_or_none()

        if existing_account:
            if existing_account.user_id != user.id:
                raise ValueError(f"该 {provider.title()} 账号已绑定其他用户")
            account = existing_account
        else:
            account = ThirdPartyAccount(
                provider=provider,
                user_id=user.id,
                **profile,
            )

        self.update_account_snapshot(account, profile)
        self.session.add(account)
        return account

    def unbind_third_party_account(self, provider: str, user: User):
        account = ThirdPartyAccount.query.filter_by(
            provider=provider, user_id=user.id
        ).one_or_none()
        if not account:
            raise ValueError(f"未找到已绑定的 {provider} 账号")

        bind_count = ThirdPartyAccount.query.filter_by(user_id=user.id).count()
        if not user.has_password and bind_count <= 1:
            raise ValueError("解绑失败：您未设置密码，且这是您唯一的登录方式。请先设置密码或绑定其他登录方式。")

        self.session.delete(account)
