"""
用户数据校验模型
"""
from .auth_schemas import (
    BindEmailRequest,
    ChangeEmailRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    RegisterRequest,
)

__all__ = [
    "RegisterRequest",
    "ChangePasswordRequest",
    "ForgotPasswordRequest",
    "BindEmailRequest",
    "ChangeEmailRequest",
]
