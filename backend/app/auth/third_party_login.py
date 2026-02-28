from __future__ import annotations

import json
import logging
import re
import secrets
from datetime import timedelta
from typing import Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from flask import redirect, request, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    decode_token,
    jwt_required,
)

from ..infrastructure.database.redis import redis
from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.oauth import (
    OAuthInfraService,
    get_frontend_oauth_redirect,
    has_oauth_network_error_message,
)
from ..models import ThirdPartyAccount, User
from ..utils.response import error, success
from . import auth

oauth_infra_service = OAuthInfraService(redis_client=redis)
FRONTEND_OAUTH_REDIRECT = get_frontend_oauth_redirect()


def _safe_profile(raw_profile) -> Optional[Dict]:
    """确保 raw_profile 可序列化为 JSON"""
    if raw_profile is None:
        return None
    try:
        return json.loads(json.dumps(raw_profile, default=str))
    except Exception as exc:  # noqa: BLE001
        logging.warning("原始第三方资料序列化失败: %s", exc)
        return None


def _extract_auth_user_profile(auth_user) -> Dict:
    """
    从 AuthUser 对象中提取标准化的用户资料

    返回:
        Dict: 包含所有标准化字段的字典
    """
    return {
        "uuid": getattr(auth_user, "uuid", None),
        "username": getattr(auth_user, "username", None),
        "nickname": getattr(auth_user, "nickname", None),
        "avatar": getattr(auth_user, "avatar", None),
        "email": getattr(auth_user, "email", None),
        "mobile": getattr(auth_user, "mobile", None),
        "gender": auth_user.gender.value if auth_user.gender else None,
        "location": getattr(auth_user, "location", None),
        "company": getattr(auth_user, "company", None),
        "blog": getattr(auth_user, "blog", None),
        "remark": getattr(auth_user, "remark", None),
        "raw_user_info": _safe_profile(getattr(auth_user, "raw_user_info", None)),
    }


def _generate_username(base_name: str) -> str:
    """
    基于第三方昵称生成唯一用户名。
    """
    slug = re.sub(r"[^a-zA-Z0-9_]+", "", base_name or "").lower() or "user"
    candidate = slug
    index = 1
    while User.query.filter_by(username=candidate).first():
        candidate = f"{slug}{index}"
        index += 1
    return candidate


def _get_or_create_user(provider: str, auth_user) -> User:
    """将第三方账号落地到 User + ThirdPartyAccount"""
    profile = _extract_auth_user_profile(auth_user)

    uuid = profile.get("uuid")
    if not uuid:
        raise ValueError("第三方登录缺少 uuid")

    account = ThirdPartyAccount.query.filter_by(
        provider=provider, uuid=uuid
    ).one_or_none()

    if account:
        # 已绑定用户，更新快照信息
        _update_account_snapshot(account, profile)
        db.session.add(account)
        user = User.query.get(account.user_id)
        if user and (not user.image and profile["avatar"]):
            user.image = profile["avatar"]
            db.session.add(user)
        return user

    # 创建用户
    username = _generate_username(profile["username"])
    user = User(
        username=username,
        nickname=profile["nickname"],
        image=profile["avatar"],
        # 生成不可预测的密码，防止密码登录
        password=secrets.token_urlsafe(32),
        # 用户不具备密码登陆能力
        has_password=False,
    )
    db.session.add(user)
    # 获取 user.id
    db.session.flush()

    account = ThirdPartyAccount(
        provider=provider,
        user_id=user.id,
        **profile,
    )
    db.session.add(account)
    return user


def _update_account_snapshot(account: ThirdPartyAccount, profile: Dict) -> None:
    """
    更新第三方账号快照信息

    参数:
        account: ThirdPartyAccount 对象
        profile: 标准化的用户资料字典
    """
    account.nickname = profile["nickname"]
    account.avatar = profile["avatar"]
    account.email = profile["email"]
    account.mobile = profile["mobile"]
    account.gender = profile["gender"]
    account.location = profile["location"]
    account.company = profile["company"]
    account.blog = profile["blog"]
    account.remark = profile["remark"]
    account.raw_user_info = profile["raw_user_info"]


def _bind_third_party_account(
    provider: str, auth_user, user: User = None
) -> Optional[ThirdPartyAccount]:
    """
    将第三方账号绑定到指定用户

    参数:
        provider: 第三方平台名称
        auth_user: 第三方用户信息
        user: 要绑定的本地用户（可选，如果不传则使用current_user）

    返回:
        ThirdPartyAccount: 绑定成功的账号记录
        None: 绑定失败
    """
    if user is None:
        user = current_user
        if not user or not user.is_authenticated:
            raise ValueError("用户未登录，无法绑定第三方账号")

    profile = _extract_auth_user_profile(auth_user)
    uuid = profile.get("uuid")
    if not uuid:
        raise ValueError("第三方登录缺少 uuid")

    # 检查该第三方账号是否已被其他用户绑定
    existing_account = ThirdPartyAccount.query.filter_by(
        provider=provider, uuid=uuid
    ).one_or_none()

    if existing_account:
        if existing_account.user_id != user.id:
            # 已被其他用户绑定
            raise ValueError(f"该 {provider.title()} 账号已绑定其他用户")
        else:
            # 已绑定到当前用户，更新信息即可（幂等）
            account = existing_account
    else:
        # 创建新的绑定记录
        account = ThirdPartyAccount(
            provider=provider,
            user_id=user.id,
            **profile,
        )

    # 更新快照信息
    _update_account_snapshot(account, profile)

    db.session.add(account)
    return account


@auth.route("/oauth/providers", methods=["GET"])
def list_oauth_providers():
    """
    返回已启用的平台列表，前端据此动态渲染按钮。
    """
    providers = []
    for provider in oauth_infra_service.enabled_providers():
        providers.append(
            {
                "provider": provider,
                "name": oauth_infra_service.oauth_configs[provider].get(
                    "display_name", provider.title()
                ),
                "authorize_endpoint": url_for(
                    "auth.oauth_authorize", provider=provider, _external=False
                ),
            }
        )
    return success(data={"providers": providers})


@auth.route("/oauth/authorize/<provider>", methods=["GET"])
def oauth_authorize(provider: str):
    """
    返回第三方授权地址（由前端跳转）。
    """
    try:
        auth_request, _ = oauth_infra_service.get_auth_request(provider)
        auth_url = auth_request.authorize()

        # 查询参数进行ENCODE编码
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        encoded_query = urlencode(query_params, doseq=True)
        encoded_url = parsed._replace(query=encoded_query).geturl()

        return success(data={"authorize_url": encoded_url, "provider": provider})
    except Exception as exc:  # noqa: BLE001
        logging.exception("创建授权请求失败: %s", exc)
        return error(code=400, message=str(exc))


def _handle_oauth_error(
    provider: str, error_code: int, error_message: str, is_bind: bool = False
):
    """
    统一处理 OAuth 错误，根据是否有前端重定向地址决定返回方式

    Args:
        provider: 第三方平台名称
        error_code: HTTP 错误码
        error_message: 错误消息
        is_bind: 是否为绑定模式

    Returns:
        redirect 或 error 响应
    """
    if FRONTEND_OAUTH_REDIRECT:
        # 如果有前端重定向地址，跳转到前端并传递错误信息
        query = urlencode(
            {
                "provider": provider,
                "status": "error",
                "message": error_message,
                **({"action": "bind"} if is_bind else {}),
            }
        )
        return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")

    # 否则直接返回 JSON 错误
    return error(code=error_code, message=error_message)


@auth.route("/oauth/callback/<provider>", methods=["GET"])
def oauth_callback(provider: str):
    """
    第三方回调：
    - 统一解析第三方用户
    - 落库（User / ThirdPartyAccount）
    - 签发 JWT，并跳转到前端处理页面
    """
    params = dict(request.args)
    is_bind_mode = False
    try:
        auth_request, meta = oauth_infra_service.get_auth_request(provider)
        logging.info(
            "处理第三方回调 provider=%s redirect_uri=%s params=%s",
            provider,
            meta["redirect_uri"],
            params,
        )

        try:
            auth_user_response = auth_request.login(params)
        except requests.exceptions.ConnectionError as e:
            # 网络连接错误（服务器无法访问外网）
            logging.error(
                f"OAuth 网络连接失败 provider={provider}, error={str(e)}",
                exc_info=True,
            )
            return _handle_oauth_error(
                provider,
                503,
                f"{provider.title()} 服务连接失败，请稍后重试或检查网络配置",
            )
        except requests.exceptions.Timeout as e:
            # 请求超时
            logging.error(f"OAuth 请求超时 provider={provider}, error={str(e)}")
            return _handle_oauth_error(
                provider,
                504,
                f"{provider.title()} 服务响应超时，请稍后重试",
            )
        except AttributeError as e:
            raise

        # 检查响应是否包含网络错误（即使 code=200，message 中也可能包含错误）
        if has_oauth_network_error_message(auth_user_response.message):
            # 网络错误
            logging.error(f"OAuth 网络错误从响应中检测到: {auth_user_response.message}")
            return _handle_oauth_error(
                provider,
                503,
                f"{provider.title()} 服务连接失败，请稍后重试或检查网络配置",
            )

        if auth_user_response.code != 200 or not auth_user_response.data:
            return error(
                code=auth_user_response.code or 400,
                message=auth_user_response.message or "第三方登录失败",
            )

        auth_user = auth_user_response.data
        if getattr(auth_user, "service_url", None):
            # 个别平台需要前往服务页面
            return redirect(auth_user.service_url)

        # 检查是否为绑定模式（通过state参数判断）
        state = params.get("state", "")
        is_bind_mode = state.startswith("bind:")

        if is_bind_mode:
            # 绑定模式：需要用户已登录
            try:
                # 从state中提取token
                token = state[5:]  # 移除 "bind:" 前缀
                decoded_token = decode_token(token, allow_expired=False)
                user_id = decoded_token.get("sub")

                # 获取用户
                user = User.query.get(user_id)
                if not user:
                    raise ValueError("用户不存在")

                # 执行绑定
                account = _bind_third_party_account(provider, auth_user, user)
                db.session.commit()

                # 绑定成功，返回结果
                if FRONTEND_OAUTH_REDIRECT:
                    query = urlencode(
                        {
                            "provider": provider,
                            "action": "bind",
                            "status": "success",
                            "message": "绑定成功",
                        }
                    )
                    return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")

                return success(message="绑定成功")

            except Exception as exc:
                logging.exception("绑定第三方账号失败: %s", exc)
                db.session.rollback()
                error_message = str(exc) if str(exc) else "绑定失败"

                if FRONTEND_OAUTH_REDIRECT:
                    query = urlencode(
                        {
                            "provider": provider,
                            "action": "bind",
                            "status": "error",
                            "message": error_message,
                        }
                    )
                    return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")

                return error(code=400, message=error_message)
        else:
            # 正常登录/注册模式
            user = _get_or_create_user(provider, auth_user)
            db.session.commit()

            # 登录态
            user_payload = user.to_json()
            access_token = "Bearer " + create_access_token(identity=user, fresh=True)
            refresh_token = "Bearer " + create_refresh_token(identity=user)

            # 更新最近活跃
            user.ping()

            # 返回给前端
            if FRONTEND_OAUTH_REDIRECT:
                query = urlencode(
                    {
                        "provider": provider,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": json.dumps(user_payload),
                    }
                )
                return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")

            return success(
                data=user_payload,
                access_token=access_token,
                refresh_token=refresh_token,
                message="登录成功",
            )
    except requests.exceptions.ConnectionError as e:
        # 网络连接错误（服务器无法访问外网）- 在最外层捕获兜底
        logging.error(
            f"OAuth 网络连接失败(外层捕获) provider={provider}, error={str(e)}",
            exc_info=True,
        )
        return _handle_oauth_error(
            provider,
            503,
            f"服务器无法连接 {provider.title()} 服务，请稍后重试或联系管理员检查网络配置",
            is_bind_mode,
        )
    except requests.exceptions.Timeout as e:
        logging.error(f"OAuth 请求超时(外层捕获) provider={provider}, error={str(e)}")
        return _handle_oauth_error(
            provider,
            504,
            f"连接 {provider.title()} 服务超时，请稍后重试",
            is_bind_mode,
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("处理第三方登录失败: %s", exc)
        db.session.rollback()
        return _handle_oauth_error(
            provider,
            500,
            "处理第三方登录失败，请稍后重试",
            is_bind_mode,
        )


@auth.route("/oauth/bind/<provider>", methods=["POST"])
@jwt_required()
def oauth_bind(provider: str):
    """
    发起第三方账号绑定

    返回第三方授权地址，前端需要跳转该地址
    """
    try:
        # 检查平台是否支持
        if provider not in oauth_infra_service.enabled_providers():
            return error(code=400, message=f"不支持的平台: {provider}")

        auth_request, _ = oauth_infra_service.get_auth_request(provider)

        # 生成包含用户token的state参数，用于绑定模式
        # 格式: bind:<user_jwt_token>
        # 使用较短的过期时间（10分钟）

        user_token = create_access_token(
            identity=current_user, expires_delta=timedelta(minutes=10), fresh=False
        )
        bind_state = f"bind:{user_token}"

        # 获取授权URL（包含state参数）
        auth_url = auth_request.authorize(state=bind_state)

        return success(data={"authorize_url": auth_url, "provider": provider})
    except Exception as exc:
        logging.exception("发起第三方账号绑定失败: %s", exc)
        return error(code=500, message=f"发起绑定失败: {str(exc)}")


@auth.route("/oauth/unbind/<provider>", methods=["POST"])
@jwt_required()
def oauth_unbind(provider: str):
    """
    解绑第三方账号

    规则：
    1. 只能解绑已绑定到当前用户的第三方账号
    2. 若用户没有密码且当前第三方是唯一登录方式，禁止解绑
    """
    try:
        # 查询该第三方账号的绑定记录
        account = ThirdPartyAccount.query.filter_by(
            provider=provider, user_id=current_user.id
        ).one_or_none()

        if not account:
            return error(code=404, message=f"未找到已绑定的 {provider} 账号")

        # 检查是否可以解绑（至少保留一种登录方式）
        # 条件：该用户不具备密码登录能力 且 只有这一个第三方绑定
        bind_count = ThirdPartyAccount.query.filter_by(user_id=current_user.id).count()

        if not current_user.has_password and bind_count <= 1:
            return error(code=400, message="解绑失败：您未设置密码，且这是您唯一的登录方式。请先设置密码或绑定其他登录方式。")

        # 执行解绑
        db.session.delete(account)
        db.session.commit()

        return success(message=f"已成功解绑 {provider.title()} 账号")

    except Exception as exc:
        logging.exception("解绑第三方账号失败: %s", exc)
        db.session.rollback()
        return error(code=500, message=f"解绑失败: {str(exc)}")
