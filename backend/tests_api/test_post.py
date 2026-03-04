import time
from base64 import b64encode

from app.infrastructure.persistence.models import Role


class TestApiCase:
    pre_fix = "/api/v1"

    def test_no_auth(self, client):
        r = client.get(self.pre_fix + "/posts", content_type="application/json")
        assert r.status_code == 200
        assert r.json.get("code") == 200

    def test_posts(self, client, auth):
        """模拟新用户注册、登陆，发布普通文章，图文，markdown文章的过程"""
        auth_instance = auth()
        r = Role.query.filter_by(name="User").first()
        assert r
        # 注册并验证成功
        register_response = auth_instance.register()
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录并验证成功
        login_response = auth_instance.login()
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None
        # 发布普通文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=auth_instance.get_headers(),
            json={"content": "666", "type": "text", "images": []},
        )
        assert r.json.get("code") == 200

        # 获取刚刚发布的文章
        r = client.get(self.pre_fix + "/posts", headers=auth_instance.get_headers())
        assert r.status_code == 200
        assert r.json.get("data")[0].get("summary") == "666"
        assert r.json.get("data")[0].get("author") == "test"

        time.sleep(1)
        # 发布图文文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=auth_instance.get_headers(),
            json={
                "content": "测试图文文章",
                "images": ["123.png", "456.png"],
                "type": "text",
            },
        )
        assert r.json.get("code") == 200
        data = r.json.get("data")
        assert "测试图文文章" in data[0].get("summary")
        assert len(data[0].get("post_images")) == 2

        time.sleep(1)
        # 发布markdown文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=auth_instance.get_headers(),
            json={
                "content": "测试markdown文章[图片](1)",
                "images": [{"url": "abc.png", "pos": 1}, {"url": "efg.png", "pos": 2}],
                "type": "markdown",
            },
        )
        assert r.json.get("code") == 200
        assert r.json.get("total") == 3
        data = r.json.get("data")
        assert "测试markdown文章" in data[0].get("summary")
        assert "1" in data[0].get("pos")
