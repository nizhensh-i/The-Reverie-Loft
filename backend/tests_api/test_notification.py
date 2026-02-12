from base64 import b64encode


class TestNotificationCase:
    """测试通知推送功能"""

    pre_fix = "/api/v1"

    def test_comment_notification(self, client, auth):
        """测试评论通知"""
        # 1. 创建两个独立的认证实例
        auth_a = auth()
        auth_b = auth()

        # 注册并登录作者 (User A)
        auth_a.register(username="author1", password="password")
        login_a = auth_a.login(username="author1", password="password")
        assert login_a.status_code == 200
        assert login_a.get_json().get("code") == 200

        # 发布文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=auth_a.get_headers(),
            json={"content": "测试文章内容", "type": "text", "images": []},
        )
        assert r.get_json().get("code") == 200
        # 根据你后端的返回结构获取 ID，通常在 data 列表或对象中
        post_id = r.get_json().get("data")[0].get("id")

        # 注册并登录评论者 (User B)
        auth_b.register(username="commenter1", password="password")
        auth_b.login(username="commenter1", password="password")

        # User B 评论 User A 的文章
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth_b.get_headers(),
            json={"body": "这是一条测试评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200

        # User A 查看通知
        r = client.get(self.pre_fix + "/notifications", headers=auth_a.get_headers())
        assert r.get_json().get("code") == 200

        notifications = r.get_json().get("data")
        assert len(notifications) > 0
        assert notifications[0].get("type") == "评论"
        assert notifications[0].get("triggerUsername") == "commenter1"

    def test_like_notification(self, client, auth):
        """测试点赞通知"""
        auth_author = auth()
        auth_liker = auth()

        # 作者发布文章
        auth_author.register(username="author2", password="password")
        auth_author.login(username="author2", password="password")

        r = client.post(
            self.pre_fix + "/posts",
            headers=auth_author.get_headers(),
            json={"content": "测试文章内容", "type": "text", "images": []},
        )
        post_id = r.get_json().get("data")[0].get("id")

        # 点赞者登录
        auth_liker.register(username="liker2", password="password")
        auth_liker.login(username="liker2", password="password")

        # 点赞操作
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/likes", headers=auth_liker.get_headers()
        )
        assert r.get_json().get("code") == 200

        # 作者检查通知
        r = client.get(
            self.pre_fix + "/notifications", headers=auth_author.get_headers()
        )
        notifications = r.get_json().get("data")
        assert len(notifications) > 0
        assert notifications[-1].get("type") == "点赞"

    def test_reply_notification(self, client, auth):
        """测试回复通知"""
        auth_c1 = auth()
        auth_c2 = auth()

        # 用户1发帖并自评
        auth_c1.register(username="commenter3", password="password")
        auth_c1.login(username="commenter3", password="password")

        r_post = client.post(
            self.pre_fix + "/posts",
            headers=auth_c1.get_headers(),
            json={"content": "测试内容", "type": "text", "images": []},
        )
        post_id = r_post.get_json().get("data")[0].get("id")

        r_cmt = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth_c1.get_headers(),
            json={"body": "这是一条评论", "directParentId": None, "at": []},
        )
        # 假设返回的 data 是单条评论对象
        comment_id = r_cmt.get_json().get("data").get("id")

        # 用户2回复用户1的评论
        auth_c2.register(username="commenter31", password="password")
        auth_c2.login(username="commenter31", password="password")

        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth_c2.get_headers(),
            json={"body": "这是对评论的回复", "directParentId": comment_id, "at": []},
        )
        assert r.get_json().get("code") == 200

        # 用户1检查通知
        r = client.get(self.pre_fix + "/notifications", headers=auth_c1.get_headers())
        notifications = r.get_json().get("data")
        assert notifications[0].get("type") == "回复"

    def test_mark_notification_as_read(self, client, auth):
        """测试标记通知为已读"""
        auth_a = auth()
        auth_b = auth()

        # A发帖
        auth_a.register(username="author4", password="password")
        auth_a.login(username="author4", password="password")
        r_post = client.post(
            self.pre_fix + "/posts",
            headers=auth_a.get_headers(),
            json={"content": "测试内容", "type": "text", "images": []},
        )
        post_id = r_post.get_json().get("data")[0].get("id")

        # B评论
        auth_b.register(username="commenter4", password="password")
        auth_b.login(username="commenter4", password="password")
        client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth_b.get_headers(),
            json={"body": "评论", "directParentId": None, "at": []},
        )

        # A查看并标记已读
        r_notif = client.get(
            self.pre_fix + "/notifications", headers=auth_a.get_headers()
        )
        notification_id = r_notif.get_json().get("data")[-1].get("id")

        r_read = client.patch(
            self.pre_fix + "/notifications",
            headers=auth_a.get_headers(),
            json={"ids": [notification_id]},
        )
        assert r_read.get_json().get("code") == 200

        # 验证状态
        r_final = client.get(
            self.pre_fix + "/notifications", headers=auth_a.get_headers()
        )
        assert r_final.get_json().get("data")[-1].get("isRead") is True
