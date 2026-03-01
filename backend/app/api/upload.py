import logging
import os

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..services.upload_service import UploadService
from ..utils.response import bad_request, success
from . import api

upload_service = UploadService()


# --------------------------- 文件上传 ---------------------------
@api.route("/files/token", methods=["GET"])
@jwt_required()
def get_upload_token():
    """获取七牛云上传凭证"""
    logging.info("获取上传凭证")
    result = upload_service.create_upload_token()
    if not result.data.get("upload_token"):
        return bad_request("存储服务暂不可用，请稍后重试")
    return success(data=result.data)


@api.route("/files/urls", methods=["POST"])
def get_signed_image_urls():
    """获取私有存储图片url(暂时没用上)"""
    logging.info("获取签名图片URL")
    data = request.get_json()
    keys = data.get("keys", [])
    if not keys:
        return bad_request("Missing keys parameter")
    result = upload_service.list_signed_image_urls(keys=keys)
    return success(data={"signed_urls": result.data})


@api.route("/del_image", methods=["DELETE"])
@jwt_required()
def delete_image():
    """删除七牛云图片
    key格式： path/xxx.jpg
    比如：userAvatars/af8e0ade-6bc4-45d0-a5ac-dea1b098119d.jpg
    """
    logging.info(f"删除图片: user_id={current_user.id}")
    j = request.get_json()
    bucket_name = j.get("bucket")
    keys = j.get("key", [])
    if not keys:
        return bad_request("缺少要删除的图片key")
    result = upload_service.delete_images(keys=keys, bucket_name=bucket_name)
    return success(message=result.message)


@api.route("/dir_name")
def query_qiniu_key():
    """查询七牛云某个bucket指定目录的所有文件名"""
    logging.info("查询七牛云目录文件")
    prefix = request.args.get("prefix", "userBackground/static")
    current_page = int(request.args.get("currentPage", 1))
    page_size = int(request.args.get("pageSize", 6))
    complete_url = bool(int(request.args.get("completeUrl", True)))
    bucket_name = request.args.get("bucket", os.getenv("QINIU_BUCKET_NAME"))
    result = upload_service.list_dir_files(
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
    """上传兴趣封面"""
    logging.info(f"上传兴趣封面: user_id={user_id}")
    j = request.get_json()
    interest_urls = j.get("urls", [])
    interest_names = j.get("names", [])
    result = upload_service.update_interest_images(
        user_id=user_id,
        urls=interest_urls,
        names=interest_names,
        interest_type=j.get("type"),
    )
    return success(data=result.data)
