"""Application-wide exception exports."""

from .domain.common.exceptions import DomainError as AppError
from .domain.common.exceptions import ForbiddenError as PermissionDeniedError
from .domain.common.exceptions import NotFoundError, ValidationError


class BusinessError(AppError):
    default_code = 400
    default_message = "业务处理失败"


__all__ = [
    "AppError",
    "ValidationError",
    "BusinessError",
    "PermissionDeniedError",
    "NotFoundError",
]
