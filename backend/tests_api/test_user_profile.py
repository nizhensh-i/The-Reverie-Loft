from base64 import b64encode


class TestUserProfileCase:
    """测试用户资料相关功能"""

    pre_fix = "/api/v1"

    def test_get_user_profile(self, client, auth):
        """测试获取用户资料"""
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

        # 获取当前用户信息
        r = client.get(self.pre_fix + "/users/1", headers=auth_instance.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert r.json.get("data").get("username") == "test"

        # 获取不存在的用户信息
        r = client.get(self.pre_fix + "/users/999", headers=auth_instance.get_headers())
        assert r.json.get("code") == 404

    def test_update_user_profile(self, client, auth):
        """测试更新用户资料"""
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

        # 更新用户资料
        update_data = {
            "nickname": "测试昵称",
        }
        r = client.patch(
            self.pre_fix + "/users/1",
            headers=auth_instance.get_headers(),
            json=update_data,
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert "用户资料更新成功" in r.json.get("message")

        # 验证更新是否成功
        r = client.get(self.pre_fix + "/users/1", headers=auth_instance.get_headers())
        assert r.status_code == 200
        assert r.json.get("data").get("nickname") == "测试昵称"

    def test_update_user_social_account(self, client, auth):
        """测试更新用户社交账号"""
        auth_instance = auth()
        register_response = auth_instance.register()
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        login_response = auth_instance.login()
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None

        update_data = {
            "social_account": {
                "github": "https://github.com/test",
                "qq": "123456789",
                "wechat": "wx_test",
                "bilibili": "bili_test",
                "twitter": "@test",
                "tiktok": None,
                "rednote": None,
                "email": "test@example.com",
            }
        }
        r = client.patch(
            self.pre_fix + "/users/1",
            headers=auth_instance.get_headers(),
            json=update_data,
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert "用户资料更新成功" in r.json.get("message")

        r = client.get(self.pre_fix + "/users/1", headers=auth_instance.get_headers())
        assert r.status_code == 200
        social_account = r.json.get("data").get("social_account")
        assert social_account.get("qq") == "123456789"
        assert social_account.get("github") == "https://github.com/test"

    def test_follow_unfollow_user(self, client, auth):
        """测试关注和取消关注用户"""
        # 创建两个独立的认证实例
        auth_user1 = auth()
        auth_user2 = auth()

        # 注册第一个用户并验证成功
        register_response = auth_user1.register(username="user1", password="password1")
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录第一个用户并验证成功
        login_response = auth_user1.login(username="user1", password="password1")
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None
        headers_user1 = auth_user1.get_headers()

        # 注册第二个用户并验证成功
        register_response = auth_user2.register(username="user2", password="password2")
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录第二个用户并验证成功
        login_response = auth_user2.login(username="user2", password="password2")
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None
        headers_user2 = auth_user2.get_headers()

        # 获取用户ID
        r = client.get(self.pre_fix + "/users/1", headers=headers_user1)
        user1_id = r.json.get("data").get("id")
        username1 = r.json.get("data").get("username")

        r = client.get(self.pre_fix + "/users/2", headers=headers_user2)
        r.json.get("data").get("id")
        r.json.get("data").get("username")

        # user2 关注 user1
        r = client.post(
            self.pre_fix + f"/users/{username1}/follow", headers=headers_user2
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 验证关注状态
        r = client.get(self.pre_fix + f"/users/{user1_id}", headers=headers_user2)
        assert r.json.get("data").get("is_followed_by_current_user") is True

        # user2 取消关注 user1
        r = client.delete(
            self.pre_fix + f"/users/{username1}/follow", headers=headers_user2
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 验证取消关注状态
        r = client.get(self.pre_fix + f"/users/{user1_id}", headers=headers_user2)
        assert r.json.get("data").get("is_followed_by_current_user") is False
