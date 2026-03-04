"""
统一接口返回格式工具
"""
from flask import jsonify


def api_response(code=200, message="success", data=None, **kwargs):
    """
    统一API响应格式

    Args:
        code (int): 状态码，默认200表示成功
        message (str): 响应消息
        data (dict/list): 响应数据
        **kwargs: 其他额外参数，如total等

    Returns:
        Response: Flask响应对象，JSON格式
    """
    if data is None:
        data = {}

    response = {"code": code, "message": message, "data": data}

    # 添加额外参数
    for key, value in kwargs.items():
        response[key] = value

    return jsonify(response)


def success(data=None, message="success", **kwargs):
    """成功响应"""
    return api_response(200, message, data, **kwargs)


def error(code=400, message="error", data=None, **kwargs):
    """错误响应"""
    return api_response(code, message, data, **kwargs)


def bad_request(message="参数错误", data=None):
    """400错误"""
    return api_response(400, message, data)


def unauthorized(message="未授权", data=None):
    """401错误"""
    return api_response(401, message, data)


def forbidden(message="禁止访问", data=None):
    """403错误"""
    return api_response(403, message, data)


def not_found(message="资源不存在", data=None):
    """404错误"""
    return api_response(404, message, data)


def too_many_req(message="操作过于频繁", data=None):
    """429错误"""
    return api_response(429, message, data)


def server_error(message="服务器内部错误", data=None):
    """500错误"""
    return api_response(500, message, data)


def too_many_req(message="请求频率超限", data=None):
    """429错误"""
    return api_response(429, message, data)
