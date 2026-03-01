from ...models import Permission
from ..common.exceptions import ForbiddenError


def ensure_can_edit_post(operator, post):
    if operator.username != post.author.username and not operator.can(Permission.ADMIN):
        raise ForbiddenError("没有权限编辑此文章")
