"""
用户相关的Pydantic数据校验模型
"""
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """注册请求校验模型"""

    username: str = Field(..., min_length=3, max_length=16, description="用户名")
    password: str = Field(..., min_length=3, max_length=16, description="密码")
    email: str = Field("", description="邮箱地址")
    # email: EmailStr = Field(..., description="邮箱地址")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        # if not re.search(r'[A-Za-z]', v):
        #     raise ValueError('密码必须包含至少一个字母')
        # if not re.search(r'\d', v):
        #     raise ValueError('密码必须包含至少一个数字')
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v == "":
            return v
        # 只在非空时校验邮箱格式
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("邮箱格式不正确")
        return v


class ChangePasswordRequest(BaseModel):
    """修改密码请求校验模型"""

    old_password: str = Field(None, min_length=3, description="原密码（可选，当token新鲜时不需要）")
    new_password: str = Field(..., min_length=3, max_length=16, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        # if not re.search(r'[A-Za-z]', v):
        #     raise ValueError('新密码必须包含至少一个字母')
        # if not re.search(r'\d', v):
        #     raise ValueError('新密码必须包含至少一个数字')
        return v


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求校验模型"""

    email: EmailStr = Field(..., description="邮箱地址")
    new_password: str = Field(..., min_length=3, max_length=16, description="新密码")
    code: str = Field(..., min_length=4, max_length=10, description="验证码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        # if not re.search(r'[A-Za-z]', v):
        #     raise ValueError('新密码必须包含至少一个字母')
        # if not re.search(r'\d', v):
        #     raise ValueError('新密码必须包含至少一个数字')
        return v

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("验证码必须为数字")
        return v


class BindEmailRequest(BaseModel):
    """绑定邮箱请求校验模型"""

    email: EmailStr = Field(..., description="邮箱地址")
    code: str = Field(..., min_length=4, max_length=10, description="验证码")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("验证码必须为数字")
        return v


class ChangeEmailRequest(BaseModel):
    """修改邮箱请求校验模型"""

    new_email: EmailStr = Field(..., description="新邮箱地址")
    code: str = Field(..., min_length=4, max_length=10, description="验证码")
    password: str = Field(..., min_length=3, max_length=16, description="密码")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("验证码必须为数字")
        return v
