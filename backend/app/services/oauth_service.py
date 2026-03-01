import json
import logging
import re
import secrets
from typing import Dict, Optional

from ..domain.common.exceptions import NotFoundError, ValidationError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.oauth.policies import ensure_oauth_user_uuid


class OAuthAccountService:
    def __init__(self, *, uow: UnitOfWork):
        self.uow = uow

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
        while self.uow.oauth.username_exists(candidate):
            candidate = f"{slug}{index}"
            index += 1
        return candidate

    @staticmethod
    def update_account_snapshot(account, profile: Dict) -> None:
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

    def get_or_create_user(self, provider: str, auth_user):
        profile = self.extract_auth_user_profile(auth_user)
        uuid = profile.get("uuid")
        ensure_oauth_user_uuid(uuid)

        account = self.uow.oauth.get_account_by_provider_uuid(
            provider=provider, uuid=uuid
        )

        if account:
            self.update_account_snapshot(account, profile)
            self.uow.oauth.add(account)
            user = self.uow.oauth.get_user_by_id(account.user_id)
            if user and (not user.image and profile["avatar"]):
                user.image = profile["avatar"]
                self.uow.oauth.add(user)
            return user

        username = self.generate_username(profile["username"])
        user = self.uow.oauth.create_user(
            username=username,
            nickname=profile["nickname"],
            image=profile["avatar"],
            password=secrets.token_urlsafe(32),
            has_password=False,
        )
        self.uow.oauth.add(user)
        self.uow.flush()
        self.uow.follows.add(
            self.uow.follows.create_follow_relation(
                follower_id=user.id,
                followed_id=user.id,
            )
        )

        account = self.uow.oauth.create_account(
            provider=provider,
            user_id=user.id,
            profile=profile,
        )
        self.uow.oauth.add(account)
        return user

    def bind_third_party_account(self, provider: str, auth_user, user):
        profile = self.extract_auth_user_profile(auth_user)
        uuid = profile.get("uuid")
        ensure_oauth_user_uuid(uuid)

        existing_account = self.uow.oauth.get_account_by_provider_uuid(
            provider=provider, uuid=uuid
        )

        if existing_account:
            if existing_account.user_id != user.id:
                raise ValidationError(f"该 {provider.title()} 账号已绑定其他用户")
            account = existing_account
        else:
            account = self.uow.oauth.create_account(
                provider=provider,
                user_id=user.id,
                profile=profile,
            )

        self.update_account_snapshot(account, profile)
        self.uow.oauth.add(account)
        return account

    def unbind_third_party_account(self, provider: str, user):
        account = self.uow.oauth.get_account_by_provider_user(
            provider=provider, user_id=user.id
        )
        if not account:
            raise NotFoundError(f"未找到已绑定的 {provider} 账号")

        bind_count = self.uow.oauth.count_user_accounts(user_id=user.id)
        if not user.has_password and bind_count <= 1:
            raise ValidationError("解绑失败：您未设置密码，且这是您唯一的登录方式。请先设置密码或绑定其他登录方式。")

        self.uow.oauth.delete(account)
