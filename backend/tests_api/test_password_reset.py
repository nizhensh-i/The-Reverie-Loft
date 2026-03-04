# from app.infrastructure.persistence.models import User, Role
# from app import redis
from base64 import b64encode


class TestPasswordResetCase:
    """测试密码重置流程"""

    def test_change_password(self, client, auth):
        """测试修改密码"""
        auth_instance = auth()
        # 注册并验证成功
        register_response = auth_instance.register()
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录并验证成功
        login_response = auth_instance.login()
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None

        # 修改密码
        r = client.post(
            "/auth/changePassword",
            headers=auth_instance.get_headers(),
            json={"old_password": "test", "new_password": "new_password"},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 使用旧密码登录应该失败
        r = client.post(
            "/auth/login", json={"uiAccountName": "test", "uiPassword": "test"}
        )
        assert r.json.get("code") == 400

        # 使用新密码登录应该成功
        r = client.post(
            "/auth/login", json={"uiAccountName": "test", "uiPassword": "new_password"}
        )
        assert r.json.get("code") == 200
        assert "access_token" in r.json

    # def test_password_reset_flow(self, client, auth, monkeypatch):
    #     """测试忘记密码流程"""
    #     # 注册用户并确保邮箱已绑定
    #     auth.register('tree', 'tree')
    #     auth.login('tree', 'tree')

    #     # 模拟验证码生成，始终返回固定验证码
    #     def mock_generate_code(email, expiration=60*3):
    #         return '123456'

    #     # 模拟验证码比较，始终返回True
    #     def mock_compare_code(email, code):
    #         return True

    #     # 模拟redis删除值
    #     def mock_delete_code(email):
    #         pass

    #     # 应用模拟函数
    #     monkeypatch.setattr(User, 'generate_code', mock_generate_code)
    #     monkeypatch.setattr(User, 'compare_code', mock_compare_code)
    #     monkeypatch.setattr(redis, 'delete', mock_delete_code)

    #     # 绑定邮箱
    #     r = client.post('/auth/applyCode', headers=auth.get_headers(), json={
    #         'email': 'test@example.com',
    #         'action': 'confirm'
    #     })
    #     assert r.status_code == 200
    #     assert r.json.get('code') == 200

    #     # 确认邮箱
    #     r = client.post('/auth/confirm', headers=auth.get_headers(), json={
    #         'email': 'test@example.com',
    #         'code': '123456'
    #     })
    #     assert r.status_code == 200
    #     assert r.json.get('code') == 200
    #     assert r.json.get('data').get('isConfirmed') == True

    #     # 申请重置密码验证码
    #     r = client.post('/auth/applyCode', json={
    #         'email': 'test@example.com',
    #         'action': 'reset'
    #     })
    #     assert r.status_code == 200
    #     assert r.json.get('code') == 200

    #     # 重置密码
    #     r = client.post('/auth/resetPassword', json={
    #         'email': 'test@example.com',
    #         'code': '123456',
    #         'password': 'reset_password'
    #     })
    #     assert r.status_code == 200
    #     assert r.json.get('code') == 200

    #     # 使用新密码登录
    #     r = client.post('/auth/login', json={
    #         'uiAccountName': 'tree',
    #         'uiPassword': 'reset_password'
    #     })
    #     assert r.json.get('code') == 200
    #     assert 'access_token' in r.json
