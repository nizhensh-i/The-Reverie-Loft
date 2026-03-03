import logging
import os

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..domain.upload.policies import (
    can_access_storage_prefix,
    can_manage_storage_keys,
    normalize_storage_keys,
)
from ..services.upload_service import UploadService
from ..utils.response import bad_request, forbidden, success
from . import api


@inject
def _upload_service(
    upload_service: UploadService = Provide[AppContainer.upload_service],
) -> UploadService:
    return upload_service


def _is_admin(user) -> bool:
    return bool(user and user.is_administrator())


def _allow_dev_prefix() -> bool:
    return os.getenv("FLASK_CONFIG") in {"development", "testing"}


@api.route("/files/token", methods=["GET"])
@jwt_required()
def get_upload_token():
    logging.info("获取上传凭证")
    result = _upload_service().create_upload_token()
    if not result.data.get("upload_token"):
        return bad_request("存储服务暂不可用，请稍后重试")
    return success(data=result.data)


@api.route("/files/urls", methods=["POST"])
def get_signed_image_urls():
    logging.info("获取签名图片URL")
    data = request.get_json() or {}
    keys = data.get("keys", [])
    if not keys:
        return bad_request("Missing keys parameter")
    result = _upload_service().list_signed_image_urls(keys=keys)
    return success(data={"signed_urls": result.data})


@api.route("/del_image", methods=["DELETE"])
@jwt_required()
def delete_image():
    logging.info("删除图片: user_id=%s", current_user.id)
    payload = request.get_json() or {}
    keys = normalize_storage_keys(payload.get("key", []))
    if not keys:
        return bad_request("缺少要删除的图片key")

    if not can_manage_storage_keys(
        user_id=current_user.id,
        is_admin=_is_admin(current_user),
        keys=keys,
        allow_dev_prefix=_allow_dev_prefix(),
    ):
        return forbidden("没有权限删除该图片")

    bucket_name = payload.get("bucket") if _is_admin(current_user) else None
    result = _upload_service().delete_images(keys=keys, bucket_name=bucket_name)
    return success(message=result.message)


@api.route("/dir_name")
@jwt_required()
def query_qiniu_key():
    logging.info("查询七牛云目录文件")
    prefix = request.args.get("prefix", "userBackground/static")
    if not can_access_storage_prefix(
        user_id=current_user.id,
        is_admin=_is_admin(current_user),
        prefix=prefix,
        allow_dev_prefix=_allow_dev_prefix(),
    ):
        return forbidden("没有权限访问该目录")

    current_page = int(request.args.get("currentPage", 1))
    page_size = int(request.args.get("pageSize", 6))
    complete_url = bool(int(request.args.get("completeUrl", True)))
    bucket_name = request.args.get("bucket") if _is_admin(current_user) else None

    result = _upload_service().list_dir_files(
        prefix=prefix,
        current_page=current_page,
        page_size=page_size,
        complete_url=complete_url,
        bucket_name=bucket_name,
    )
    return success(data=result.data, total=result.total)


@api.route("/user/<int:user_id>/interest_images", methods=["POST"])
@jwt_required()
def upload_favorite_book_image(user_id):
    logging.info("上传兴趣封面: user_id=%s", user_id)
    if not (_is_admin(current_user) or current_user.id == user_id):
        return forbidden("没有权限上传该用户的兴趣封面")

    payload = request.get_json() or {}
    interest_urls = payload.get("urls", [])
    interest_names = payload.get("names", [])
    result = _upload_service().update_interest_images(
        user_id=user_id,
        urls=interest_urls,
        names=interest_names,
        interest_type=payload.get("type"),
    )
    return success(data=result.data)
