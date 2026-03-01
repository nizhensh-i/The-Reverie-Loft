from ..common.constants import PermissionCode, PostTypeCode
from ..common.exceptions import ForbiddenError, ValidationError
from ..text.markdown_truncate import MarkdownTruncator


def ensure_can_edit_post(operator, post):
    if operator.username != post.author.username and not operator.can(
        PermissionCode.ADMIN
    ):
        raise ForbiddenError("没有权限编辑此文章")


def validate_post_content(content: str, *, min_length: int = 3):
    if len((content or "").strip()) < min_length:
        raise ValidationError(f"内容长度至少需要{min_length}个字符")


def normalize_post_type(post_type: str):
    if post_type == "markdown":
        return PostTypeCode.MARKDOWN
    # 兼容原逻辑: text/image 都存为 TEXT
    return PostTypeCode.TEXT


def build_post_summary(content: str):
    return MarkdownTruncator.get_smart_preview(content or "")


def build_post_image_entities(*, post_id: int, images):
    if not images:
        return []

    first_item = images[0]
    if isinstance(first_item, dict):
        return [
            {
                "url": image.get("url", ""),
                "type": "post",
                "describe": image.get("pos", ""),
                "related_id": post_id,
            }
            for image in images
        ]

    if isinstance(first_item, str):
        return [
            {"url": image, "type": "post", "describe": "", "related_id": post_id}
            for image in images
        ]

    raise ValidationError("图片格式不正确")
