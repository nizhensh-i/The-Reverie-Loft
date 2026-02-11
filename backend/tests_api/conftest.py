import pytest
from app import create_app
from app.infrastructure import db
from app.models import Role


@pytest.fixture
def app():
    """创建并配置一个Flask应用实例用于测试

    每个测试函数都会获得一个新的应用实例和数据库
    """
    app = create_app("testing")

    # 创建应用上下文
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试命令行运行器"""
    return app.test_cli_runner()


@pytest.fixture
def flask_app_context(app):
    """提供应用上下文的夹具"""
    with app.app_context():
        yield


@pytest.fixture
def flask_pre_and_post_process(app):
    """每个测试前后处理数据库的夹具"""
    # 测试前的处理已经在app夹具中完成
    yield
    # 测试后的清理也在app夹具中完成


class AuthAction:
    def __init__(self, client):
        self._client = client
        self._access_token = None
        self._refresh_token = None

    def register(self, username="test", password="test"):
        return self._client.post(
            "/auth/register",
            json={
                "username": username,
                "password": password,
            },
        )

    def register_admin(self, username="admin", password="admin"):
        return self._client.post(
            "/auth/register",
            json={
                "email": "zmc_li@foxmail.com",
                "username": username,
                "password": password,
            },
        )

    def login(self, username="test", password="test"):
        r = self._client.post(
            "/auth/login",
            json={"uiAccountName": username, "uiPassword": password},
        )
        # 修正点：Flask test_client 的 response 没有 .json.get，需使用 .get_json()
        data = r.get_json()
        if data:
            self._access_token = data.get("access_token")
            self._refresh_token = data.get("refresh_token")  # 新
        return r

    def get_headers(self, token_type="access"):  # 新增参数
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }
        if token_type == "access" and self._access_token:
            headers["Authorization"] = self._access_token
        elif token_type == "refresh" and self._refresh_token:
            headers["Authorization"] = self._refresh_token
        return headers


# @pytest.fixture
# def auth(client):
#     """提供认证操作的夹具"""
#     return AuthAction(client)


@pytest.fixture
def auth(client):
    # 这里保持工厂模式，但测试代码必须统一调用 auth()
    def _make_auth():
        return AuthAction(client)

    return _make_auth
