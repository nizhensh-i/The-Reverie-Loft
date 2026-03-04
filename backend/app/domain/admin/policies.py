from ..common.constants import PostTypeCode
from ..common.exceptions import ValidationError


def normalize_admin_post_type(post_type: str):
    if post_type == PostTypeCode.TEXT.value:
        return PostTypeCode.TEXT
    if post_type == PostTypeCode.MARKDOWN.value:
        return PostTypeCode.MARKDOWN
    raise ValidationError("文章类型不支持")
