import json
import logging
import os
import random
import time

from flask import request
from flask_jwt_extended import current_user, jwt_required
from qiniu import Auth, BucketManager, build_batch_delete
from sqlalchemy import and_

from ..infrastructure import db
from ..models import Image, ImageType
from ..utils.common import get_avatars_url
from ..utils.response import bad_request, success
from . import api

# 初始化Auth状态
q = Auth(
    os.getenv("QINIU_ACCESS_KEY", "fdfddgfg"),
    os.getenv("QINIU_SECRET_KEY", "dfdffgfgfg"),
)
# 初始化BucketManager
bucket = BucketManager(q)


# --------------------------- 文件上传 ---------------------------
@api.route("/files/token", methods=["GET"])
@jwt_required()
def get_upload_token():
    """获取七牛云上传凭证"""
    logging.info("获取上传凭证")
    # 定义上传策略
    policy = {
        # 限制上传文件的最大尺寸，单位为字节，这里设置为 10MB
        "fsizeLimit": 10 * 1024 * 1024,
        # 设置上传凭证的有效期，单位为秒，这里设置为 1 小时
        "deadline": int(time.time()) + 3600,
        # 'callbackUrl': 'http://172.18.66.95:8082/upload_callback',
        # 'callbackBody':'filename=$(fname)&filesize=$(fsize)&blog_text=$(x:blog_text)',
        # 'callbackBodyType':'application/json'
    }
    # 生成上传凭证，传入上传策略
    token = q.upload_token(os.getenv("QINIU_BUCKET_NAME"), policy=policy)
    return success(data={"upload_token": token})


@api.route("/files/urls", methods=["POST"])
def get_signed_image_urls():
    """获取私有存储图片url(暂时没用上)"""
    logging.info("获取签名图片URL")
    data = request.get_json()
    keys = data.get("keys", [])
    if not keys:
        return bad_request("Missing keys parameter")
    signed_urls = []
    for key in keys:
        # 添加图片瘦身参数，这里以调整图片质量为 80 为例
        fops = "imageMogr2/quality/80"
        base_url = f"{os.getenv('QINIU_DOapi')}/{key}"
        # 拼接处理参数到基础 URL
        processed_url = base_url + "?" + fops
        # 生成带处理参数的签名 URL
        private_url = q.private_download_url(processed_url, expires=3600)
        signed_urls.append(private_url)
    return success(data={"signed_urls": signed_urls})


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
    del_qiniu_image(keys, bucket_name)
    return success(message="图片删除成功")


def del_qiniu_image(keys, bucket_name=os.getenv("QINIU_BUCKET_NAME")):
    """删除七牛云图片的工具函数"""
    ops = build_batch_delete(bucket_name, keys)
    bucket.batch(ops)


def dir_file_name(
    prefix="userBackground/static",
    current_page=1,
    page_size=6,
    complete_url=True,
    bucket_name=os.getenv("QINIU_BUCKET_NAME"),
):
    # 列举条目
    limit = 50

    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    j = json.loads(info.text_body)
    item_list = j.get("items")

    start = (current_page - 1) * page_size
    end = start + page_size
    return [
        get_avatars_url(item.get("key")) if complete_url else item.get("key")
        for item in item_list[start + 1 : end + 1]
    ], len(item_list) - 1


def get_random_user_avatars():
    """获取随机图像"""
    try:
        avatars, total = dir_file_name("userAvatars/", 1, 10, False)
        return avatars[random.randint(0, total - 1)]
    except Exception as e:
        logging.warning(f"注册时从七牛云随机指定图像失败，原因：{e}")
        return ""


@api.route("/dir_name")
def query_qiniu_key():
    """查询七牛云某个bucket指定目录的所有文件名"""
    logging.info("查询七牛云目录文件")
    # 前缀
    prefix = request.args.get("prefix", "userBackground/static")
    current_page = int(request.args.get("currentPage", 1))
    page_size = int(request.args.get("pageSize", 6))
    complete_url = bool(int(request.args.get("completeUrl", True)))
    # bucket名字
    bucket_name = request.args.get("bucket", os.getenv("QINIU_BUCKET_NAME"))
    data, total = dir_file_name(
        prefix, current_page, page_size, complete_url, bucket_name
    )
    return success(data=data, total=total)


@api.route("/user/<int:user_id>/interest_images", methods=["POST"])
@jwt_required()
def upload_favorite_book_image(user_id):
    """上传兴趣封面"""
    logging.info(f"上传兴趣封面: user_id={user_id}")
    j = request.get_json()
    interest_urls = j.get("urls", [])
    interest_names = j.get("names", [])
    type_url = None
    if j.get("type") == "movie":
        type_url = ImageType.MOVIE
    elif j.get("type") == "book":
        type_url = ImageType.BOOK
    # 删除上次上传的
    last_upload_images = Image.query.filter(
        and_(Image.type == type_url, Image.related_id == user_id)
    ).all()
    if last_upload_images:
        image_keys = [image.url for image in last_upload_images]
        del_qiniu_image(image_keys)
        for item in last_upload_images:
            db.session.delete(item)
        db.session.commit()
    images = [
        Image(url=url, type=type_url, describe=name, related_id=user_id)
        for url, name in zip(interest_urls, interest_names)
    ]
    if images:
        db.session.add_all(images)
        db.session.commit()
    d = [image.to_json() for image in images]
    return success(data=d)
