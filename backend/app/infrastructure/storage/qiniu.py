import json
import logging
import os
import random
import time

from qiniu import Auth, BucketManager, build_batch_delete

_auth = None
_bucket = None


def _get_auth():
    global _auth
    if _auth is None:
        _auth = Auth(
            os.getenv("QINIU_ACCESS_KEY", "fdfddgfg"),
            os.getenv("QINIU_SECRET_KEY", "dfdffgfgfg"),
        )
    return _auth


def _get_bucket():
    global _bucket
    if _bucket is None:
        _bucket = BucketManager(_get_auth())
    return _bucket


def _resolve_bucket_name(bucket_name):
    return bucket_name or os.getenv("QINIU_BUCKET_NAME")


def _default_policy():
    return {
        "fsizeLimit": 10 * 1024 * 1024,
        "deadline": int(time.time()) + 3600,
    }


def generate_upload_token(policy=None, bucket_name=None):
    """生成七牛云上传凭证"""
    policy = policy or _default_policy()
    return _get_auth().upload_token(_resolve_bucket_name(bucket_name), policy=policy)


def get_signed_image_urls(
    keys, domain=None, fops="imageMogr2/quality/80", expires=3600
):
    """生成私有存储签名URL"""
    if not keys:
        return []
    domain = domain or os.getenv("QINIU_DOMAIN") or os.getenv("QINIU_DOapi") or ""
    signed_urls = []
    for key in keys:
        base_url = f"{domain}/{key}"
        processed_url = base_url + "?" + fops
        private_url = _get_auth().private_download_url(processed_url, expires=expires)
        signed_urls.append(private_url)
    return signed_urls


def del_qiniu_image(keys, bucket_name=None):
    """批量删除七牛云图片"""
    if not keys:
        return
    ops = build_batch_delete(_resolve_bucket_name(bucket_name), keys)
    _get_bucket().batch(ops)


def _list_items(prefix, bucket_name, limit=50, marker=None, delimiter=None):
    ret, eof, info = _get_bucket().list(
        _resolve_bucket_name(bucket_name), prefix, marker, limit, delimiter
    )
    items = []
    try:
        if info and getattr(info, "text_body", None):
            items = json.loads(info.text_body).get("items", [])
        elif ret:
            items = ret.get("items", [])
    except Exception as e:
        logging.warning(f"解析七牛云列表返回失败: {e}")
        items = []
    return items


def _build_public_url(key, domain=None):
    if not key or key.startswith("http"):
        return key
    domain = domain or os.getenv("QINIU_DOMAIN") or os.getenv("QINIU_DOapi") or ""
    return f"{domain}/{key}"


def dir_file_name(
    prefix="userBackground/static",
    current_page=1,
    page_size=6,
    complete_url=True,
    bucket_name=None,
    url_builder=None,
    domain=None,
):
    """
    列举指定目录的文件名（与原逻辑保持一致：跳过第一条）
    """
    item_list = _list_items(prefix, bucket_name)
    if not item_list:
        return [], 0

    start = (current_page - 1) * page_size
    end = start + page_size
    sliced = item_list[start + 1 : end + 1]

    keys = [item.get("key") for item in sliced]
    if complete_url:
        if url_builder:
            keys = [url_builder(key) for key in keys]
        else:
            keys = [_build_public_url(key, domain=domain) for key in keys]

    total = max(len(item_list) - 1, 0)
    return keys, total


def get_random_user_avatars():
    """获取随机图像"""
    try:
        avatars, total = dir_file_name("userAvatars/", 1, 10, False)
        return avatars[random.randint(0, total - 1)]
    except Exception as e:
        logging.warning(f"注册时从七牛云随机指定图像失败，原因：{e}")
        return ""
