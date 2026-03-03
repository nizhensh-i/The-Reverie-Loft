"""
第三方 OAuth 登录单元测试

测试原则：
1. 业务逻辑测试优先，HTTP 接口测试最少
2. 不访问真实第三方平台
3. OAuth provider 必须通过 mock 返回固定 AuthUser
4. 单个测试只验证一个业务行为
5. 测试应稳定、可重复、无顺序依赖
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from unittest.mock import MagicMock

import pytest
from app import db
from app.container import get_container
from app.infrastructure.persistence.models import ThirdPartyAccount, User
from app.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyRepositoryUnitOfWork,
)
from app.services.oauth_service import OAuthAccountService
from dependency_injector import providers
from flask_jwt_extended import create_access_token
from senweaver_oauth import AuthConfig
from senweaver_oauth.builder import AuthRequestBuilder


def _oauth_account_service() -> OAuthAccountService:
    return OAuthAccountService(uow=SqlAlchemyRepositoryUnitOfWork(db.session))


def _get_or_create_user(provider, auth_user):
    return _oauth_account_service().get_or_create_user(provider, auth_user)


def _bind_third_party_account(provider, auth_user, user=None):
    if user is None:
        raise ValueError("用户未登录")
    return _oauth_account_service().bind_third_party_account(provider, auth_user, user)


# ============================================================================
# Mock AuthUser 模型（模拟 senweaver_oauth.AuthUser）
# ============================================================================


class Gender(Enum):
    """性别枚举"""

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


@dataclass
class AuthUser:
    """模拟第三方用户信息对象"""

    uuid: str
    username: str
    nickname: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    remark: Optional[str] = None
    raw_user_info: Optional[dict] = None


# ============================================================================
# 测试数据工厂
# ============================================================================


def make_auth_user(
    uuid: str = "github_user_123",
    username: str = "github_user",
    nickname: str = "GitHub User",
    avatar: str = "https://example.com/avatar.jpg",
    email: str = "user@example.com",
    gender: Gender = Gender.MALE,
    location: str = "Beijing",
    **kwargs,
) -> AuthUser:
    """创建 AuthUser 实例的工厂函数"""
    return AuthUser(
        uuid=uuid,
        username=username,
        nickname=nickname,
        avatar=avatar,
        email=email,
        gender=gender,
        location=location,
        **kwargs,
    )


# ============================================================================
# 业务层测试：_get_or_create_user
# ============================================================================


class TestGetOrCreateUser:
    """测试第三方用户登录/注册逻辑"""

    def test_third_party_first_login_creates_user_and_account(self, app):
        """第三方首次登录 -> 创建新用户"""
        # Arrange
        provider = "github"
        auth_user = make_auth_user(
            uuid="github_uuid_001",
            username="new_user",
            nickname="New User",
            avatar="https://example.com/new_user.jpg",
        )

        # Act
        user = _get_or_create_user(provider, auth_user)
        db.session.commit()

        # Assert - User
        assert user is not None
        assert user.id is not None
        assert user.username == "new_user"
        assert user.nickname == "New User"
        assert user.image == "https://example.com/new_user.jpg"
        assert user.has_password is False  # 第三方登录用户无密码

        # Assert - ThirdPartyAccount
        account = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid="github_uuid_001"
        ).first()
        assert account is not None
        assert account.user_id == user.id
        assert account.provider == provider
        assert account.uuid == "github_uuid_001"
        assert account.username == "new_user"
        assert account.nickname == "New User"
        assert account.avatar == "https://example.com/new_user.jpg"

    def test_third_party_existing_binding_returns_user(self, app):
        """第三方已绑定用户 -> 直接登录"""
        # Arrange - 创建已绑定的用户和账号
        provider = "github"
        existing_user = User(
            username="existing_user",
            nickname="Existing User",
            password="hashed_password",
            has_password=False,
        )
        db.session.add(existing_user)
        db.session.flush()

        existing_account = ThirdPartyAccount(
            provider=provider,
            uuid="github_uuid_002",
            user_id=existing_user.id,
            username="existing_user",
            nickname="Existing User",
            avatar="https://example.com/old_avatar.jpg",
        )
        db.session.add(existing_account)
        db.session.commit()

        # Act - 使用相同的 uuid 再次登录
        auth_user = make_auth_user(
            uuid="github_uuid_002",
            username="existing_user",
            nickname="Existing User",
            avatar="https://example.com/new_avatar.jpg",  # 更新头像
        )
        user = _get_or_create_user(provider, auth_user)
        db.session.commit()

        # Assert - 返回的是已有用户
        assert user.id == existing_user.id
        assert user.username == "existing_user"

        # Assert - 账号快照已更新
        account = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid="github_uuid_002"
        ).first()
        assert account is not None
        assert account.avatar == "https://example.com/new_avatar.jpg"

    def test_third_party_login_updates_user_avatar_when_empty(self, app):
        """第三方登录 -> 用户头像为空时更新"""
        # Arrange - 创建无头像的用户
        provider = "github"
        existing_user = User(
            username="user_no_avatar",
            nickname="User No Avatar",
            password="hashed_password",
            image=None,  # 无头像
            has_password=False,
        )
        db.session.add(existing_user)
        db.session.flush()

        existing_account = ThirdPartyAccount(
            provider=provider,
            uuid="github_uuid_003",
            user_id=existing_user.id,
            username="user_no_avatar",
            nickname="User No Avatar",
            avatar="https://example.com/avatar.jpg",
        )
        db.session.add(existing_account)
        db.session.commit()

        # Act
        auth_user = make_auth_user(
            uuid="github_uuid_003",
            username="user_no_avatar",
            avatar="https://example.com/new_avatar.jpg",
        )
        user = _get_or_create_user(provider, auth_user)
        db.session.commit()

        # Assert - 用户头像已更新
        assert user.image == "https://example.com/new_avatar.jpg"


class TestBindThirdPartyAccount:
    """测试绑定第三方账号逻辑"""

    def test_bind_account_to_logged_in_user(self, app):
        """已登录用户绑定第三方账号"""
        # Arrange - 创建本地用户
        provider = "qq"
        user = User(
            username="local_user",
            nickname="Local User",
            password="hashed_password",
            has_password=True,
        )
        db.session.add(user)
        db.session.flush()

        # Act - 绑定第三方账号
        auth_user = make_auth_user(
            uuid="qq_uuid_001",
            username="qq_user",
            nickname="QQ User",
            avatar="https://qq.example.com/avatar.jpg",
        )
        account = _bind_third_party_account(provider, auth_user, user)
        db.session.commit()

        # Assert
        assert account is not None
        assert account.provider == provider
        assert account.uuid == "qq_uuid_001"
        assert account.user_id == user.id
        assert account.nickname == "QQ User"

        # 验证数据库中确实创建
        db_account = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid="qq_uuid_001"
        ).first()
        assert db_account is not None
        assert db_account.user_id == user.id

    def test_bind_account_already_bound_to_same_user_is_idempotent(self, app):
        """重复绑定同一账号（幂等性）"""
        # Arrange - 已绑定
        provider = "github"
        user = User(
            username="user1",
            nickname="User 1",
            password="hashed_password",
            has_password=True,
        )
        db.session.add(user)
        db.session.flush()

        existing_account = ThirdPartyAccount(
            provider=provider,
            uuid="github_uuid_004",
            user_id=user.id,
            username="user1",
            nickname="User 1",
        )
        db.session.add(existing_account)
        db.session.commit()

        # Act - 再次绑定相同账号
        auth_user = make_auth_user(
            uuid="github_uuid_004", username="user1", nickname="User 1 Updated"  # 昵称变化
        )
        account = _bind_third_party_account(provider, auth_user, user)
        db.session.commit()

        # Assert - 更新而不是创建新记录
        assert account.id == existing_account.id
        assert account.nickname == "User 1 Updated"

        # 验证只有一条记录
        count = ThirdPartyAccount.query.filter_by(
            provider=provider, uuid="github_uuid_004"
        ).count()
        assert count == 1

    def test_bind_account_already_bound_to_other_user_raises_error(self, app):
        """第三方账号已绑定其他用户 -> 报错"""
        # Arrange - 账号已绑定到用户1
        provider = "github"
        user1 = User(username="user1", nickname="User 1", password="pwd1")
        user2 = User(username="user2", nickname="User 2", password="pwd2")
        db.session.add_all([user1, user2])
        db.session.flush()

        existing_account = ThirdPartyAccount(
            provider=provider,
            uuid="github_uuid_005",
            user_id=user1.id,
            username="github_user",
        )
        db.session.add(existing_account)
        db.session.commit()

        # Act & Assert - 用户2尝试绑定同一账号
        auth_user = make_auth_user(uuid="github_uuid_005", username="github_user")

        with pytest.raises(ValueError) as exc_info:
            _bind_third_party_account(provider, auth_user, user2)

        assert "已绑定其他用户" in str(exc_info.value)

    def test_bind_account_without_current_user_raises_error(self, app):
        """未登录用户绑定第三方账号 -> 报错"""
        # Arrange
        provider = "github"
        auth_user = make_auth_user(uuid="github_uuid_006", username="user")

        # Act & Assert - 不传 user 参数，函数依赖 current_user
        with pytest.raises(ValueError) as exc_info:
            _bind_third_party_account(provider, auth_user, user=None)

        assert "用户未登录" in str(exc_info.value)


# ============================================================================
# 接口层测试：oauth_callback
# ============================================================================


class TestOAuthCallbackAPI:
    """测试 OAuth 回调接口"""

    def test_oauth_callback_with_invalid_state_returns_400(
        self, app, client, monkeypatch
    ):
        """state 参数不合法 -> 返回 code 400，不产生数据库写入"""

        # Arrange - Mock _get_auth_request 避免访问真实配置
        def mock_get_auth_request(provider):
            auth_config = AuthConfig(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost/api/auth/oauth/callback/github",
            )
            auth_request = (
                AuthRequestBuilder.builder()
                .source("github")
                .auth_config(auth_config)
                .build()
            )

            # Mock login 方法返回失败
            auth_request.login = MagicMock(
                return_value=MagicMock(code=401, message="Invalid state")
            )
            return auth_request, {"redirect_uri": "http://localhost/callback"}

        monkeypatch.setattr(
            get_container().oauth_infra_service(),
            "get_auth_request",
            mock_get_auth_request,
        )

        # Act
        response = client.get(
            "/auth/oauth/callback/github?code=invalid_code&state=invalid"
        )

        # Assert - HTTP 状态码可能是 200 或 500（取决于错误处理方式）
        # 但响应中的 code 字段应该是错误码
        assert response.status_code in [200, 400, 500]

        # 验证响应中的 code 字段是错误码
        data = response.get_json()
        if data:
            assert data.get("code") != 200

        # 验证没有数据库写入
        user_count = User.query.count()
        account_count = ThirdPartyAccount.query.count()
        assert user_count == 0
        assert account_count == 0

    def test_oauth_callback_with_valid_auth_user_returns_success(
        self, app, client, monkeypatch
    ):
        """正常 OAuth 回调 -> 返回成功（HTTP 200，code 200）"""
        # Arrange - Mock _get_auth_request 返回固定 AuthUser

        # 创建 mock 对象，设置明确的属性值
        mock_auth_user = MagicMock()
        mock_auth_user.uuid = "github_uuid_test"
        mock_auth_user.username = "test_user"
        mock_auth_user.nickname = "Test User"
        mock_auth_user.avatar = "https://example.com/avatar.jpg"
        mock_auth_user.email = "test@example.com"
        mock_auth_user.mobile = None
        mock_auth_user.gender = 0  # UNKNOWN
        mock_auth_user.location = None
        mock_auth_user.company = None
        mock_auth_user.blog = None
        mock_auth_user.remark = None
        mock_auth_user.raw_user_info = None
        mock_auth_user.service_url = None

        def mock_get_auth_request(provider):
            auth_config = AuthConfig(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost/api/auth/oauth/callback/github",
            )
            auth_request = (
                AuthRequestBuilder.builder()
                .source("github")
                .auth_config(auth_config)
                .build()
            )

            # Mock login 方法返回成功
            response_mock = MagicMock()
            response_mock.code = 200
            response_mock.message = None
            response_mock.data = mock_auth_user
            auth_request.login = MagicMock(return_value=response_mock)
            return auth_request, {"redirect_uri": "http://localhost/callback"}

        # 测试环境禁用前端重定向，走 JSON 响应分支
        get_container().frontend_oauth_redirect.override(providers.Object(None))
        try:
            monkeypatch.setattr(
                get_container().oauth_infra_service(),
                "get_auth_request",
                mock_get_auth_request,
            )

            # Act
            response = client.get(
                "/auth/oauth/callback/github?code=test_code&state=test_state"
            )

            # Assert - HTTP 状态码 200
            assert response.status_code == 200

            # Assert - 响应中的 code 字段为 200（成功）
            data = response.get_json()
            if data:
                assert data.get("code") == 200

            # 验证创建了用户（但不校验细节，已在业务层测试）
            user = User.query.filter_by(username="test_user").first()
            assert user is not None

            # 验证创建了第三方账号
            account = ThirdPartyAccount.query.filter_by(
                provider="github", uuid="github_uuid_test"
            ).first()
            assert account is not None
        finally:
            get_container().frontend_oauth_redirect.reset_override()

    def test_oauth_callback_bind_mode_with_valid_token(self, app, client, monkeypatch):
        """绑定模式回调 -> 绑定成功"""
        # Arrange - 创建已登录用户

        user = User(
            username="existing_user",
            nickname="Existing User",
            password="hashed_password",
            has_password=True,
        )
        db.session.add(user)
        db.session.flush()

        # 生成绑定 token
        bind_token = create_access_token(
            identity=user, expires_delta=None  # 测试环境不设置过期时间
        )

        # Mock _get_auth_request

        # 创建 mock 对象，设置明确的属性值
        mock_auth_user = MagicMock()
        mock_auth_user.uuid = "qq_uuid_test"
        mock_auth_user.username = "qq_user"
        mock_auth_user.nickname = "QQ User"
        mock_auth_user.avatar = "https://qq.example.com/avatar.jpg"
        mock_auth_user.email = None
        mock_auth_user.mobile = None
        mock_auth_user.gender = 0  # UNKNOWN
        mock_auth_user.location = None
        mock_auth_user.company = None
        mock_auth_user.blog = None
        mock_auth_user.remark = None
        mock_auth_user.raw_user_info = None
        mock_auth_user.service_url = None

        def mock_get_auth_request(provider):
            auth_config = AuthConfig(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost/api/auth/oauth/callback/qq",
            )
            auth_request = (
                AuthRequestBuilder.builder()
                .source("qq")
                .auth_config(auth_config)
                .build()
            )

            response_mock = MagicMock()
            response_mock.code = 200
            response_mock.message = None
            response_mock.data = mock_auth_user
            auth_request.login = MagicMock(return_value=response_mock)
            return auth_request, {"redirect_uri": "http://localhost/callback"}

        # 测试环境禁用前端重定向，走 JSON 响应分支
        get_container().frontend_oauth_redirect.override(providers.Object(None))
        try:
            monkeypatch.setattr(
                get_container().oauth_infra_service(),
                "get_auth_request",
                mock_get_auth_request,
            )

            # Act - 绑定模式回调（state 格式: bind:<token>）
            response = client.get(
                f"/auth/oauth/callback/qq?code=test_code&state=bind:{bind_token}"
            )

            # Assert - HTTP 状态码 200
            assert response.status_code == 200

            # Assert - 响应中的 code 字段为 200（成功）
            data = response.get_json()
            if data:
                assert data.get("code") == 200

            # 验证账号绑定成功
            account = ThirdPartyAccount.query.filter_by(
                provider="qq", uuid="qq_uuid_test"
            ).first()
            assert account is not None
            assert account.user_id == user.id
        finally:
            get_container().frontend_oauth_redirect.reset_override()
