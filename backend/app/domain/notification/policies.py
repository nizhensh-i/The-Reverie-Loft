from ..common.exceptions import ValidationError


def normalize_notification_ids(ids):
    if ids is None:
        raise ValidationError("参数错误: ids 不能为空")
    if not ids:
        return []
    return list(dict.fromkeys(ids))
