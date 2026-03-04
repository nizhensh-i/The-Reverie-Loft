# Pydantic 数据校验模型使用指南

## 概述

本项目使用 Pydantic 为用户认证相关的API接口提供数据校验功能。所有校验模型都位于 `app/schemas/` 目录下。

## 可用的校验模型

### 1. RegisterRequest - 用户注册
- `username`: 用户名 (3-20字符，只能包含字母、数字、下划线)
- `password`: 密码 (6-128字符，必须包含字母和数字)
- `email`: 邮箱地址 (标准邮箱格式)

### 2. ChangePasswordRequest - 修改密码
- `old_password`: 原密码 (必填)
- `new_password`: 新密码 (6-128字符，必须包含字母和数字)

### 3. ForgotPasswordRequest - 忘记密码
- `email`: 邮箱地址 (标准邮箱格式)
- `new_password`: 新密码 (6-128字符，必须包含字母和数字)
- `code`: 验证码 (4-10位数字)

### 4. BindEmailRequest - 绑定邮箱
- `email`: 邮箱地址 (标准邮箱格式)
- `code`: 验证码 (4-10位数字)

### 5. ChangeEmailRequest - 修改邮箱
- `new_email`: 新邮箱地址 (标准邮箱格式)
- `code`: 验证码 (4-10位数字)

## 使用方法

### 在Flask路由中使用

#### 方法1: 使用装饰器（推荐）

```python
from flask import Blueprint
from app.schemas.auth_schemas import RegisterRequest
from app.utils.validation import validate_json
from app.utils.response import success

@app.route('/register', methods=['POST'])
@validate_json(RegisterRequest)
def register(validated_data):
    # validated_data 是校验后的字典数据
    username = validated_data.get('username')
    password = validated_data.get('password')
    email = validated_data.get('email')
    
    # 处理业务逻辑...
    
    return success(message="注册成功")
```

#### 方法2: 手动校验

```python
from flask import Blueprint
from app.schemas.auth_schemas import RegisterRequest
from app.utils.validation import validate_request_data
from app.utils.response import success

@app.route('/register', methods=['POST'])
def register():
    # 校验请求数据
    validated_data, error_response = validate_request_data(RegisterRequest)
    if error_response:
        return error_response
    
    # 使用校验后的数据
    username = validated_data.username
    password = validated_data.password
    email = validated_data.email
    
    # 处理业务逻辑...
    
    return success(message="注册成功")
```

### 直接使用模型校验

```python
from app.schemas.auth_schemas import RegisterRequest
from app.utils.validation import validate_json_data

data = {
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
}

validated_data, error = validate_json_data(data, RegisterRequest)
if error:
    print(f"校验失败: {error}")
else:
    print(f"校验成功: {validated_data}")
```

## 错误处理

当数据校验失败时，系统会自动返回统一的错误响应格式：

```json
{
    "code": 400,
    "message": "具体的错误信息",
    "data": null
}
```

## 运行测试

```bash
# 运行所有校验相关测试
python -m pytest tests/test_auth_schemas.py -v

# 运行集成测试
python -m pytest tests/test_validation_integration.py -v
```

## 扩展校验规则

如需添加新的校验规则，可以在相应的模型中添加 `@validator` 装饰器：

```python
@validator('username')
def validate_username(cls, v):
    if 'admin' in v.lower():
        raise ValueError('用户名不能包含admin')
    return v
