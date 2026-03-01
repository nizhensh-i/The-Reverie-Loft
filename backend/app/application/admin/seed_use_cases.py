from __future__ import annotations


class SeedUseCases:
    def __init__(self, *, uow_factory):
        self.uow_factory = uow_factory

    def generate_users_and_posts(self):
        from ...fake import Fake

        uow = self.uow_factory()
        uow.users.init_roles()
        Fake.users()
        Fake.posts()
        return {"message": "用户和文章生成成功"}
