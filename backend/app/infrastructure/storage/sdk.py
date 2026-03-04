import json
import os

from qiniu import Auth, BucketManager, build_batch_delete

_auth = None
_bucket = None


def get_auth():
    global _auth
    if _auth is None:
        access_key = os.getenv("QINIU_ACCESS_KEY")
        secret_key = os.getenv("QINIU_SECRET_KEY")
        if not access_key or not secret_key:
            raise RuntimeError("QINIU_ACCESS_KEY 或 QINIU_SECRET_KEY 未配置")
        _auth = Auth(
            access_key,
            secret_key,
        )
    return _auth


def get_bucket():
    global _bucket
    if _bucket is None:
        _bucket = BucketManager(get_auth())
    return _bucket


def build_upload_token(bucket_name, policy):
    return get_auth().upload_token(bucket_name, policy=policy)


def build_private_download_url(processed_url, expires=3600):
    return get_auth().private_download_url(processed_url, expires=expires)


def batch_delete(bucket_name, keys):
    ops = build_batch_delete(bucket_name, keys)
    return get_bucket().batch(ops)


def list_items(bucket_name, prefix, limit=50, marker=None, delimiter=None):
    ret, _eof, info = get_bucket().list(bucket_name, prefix, marker, limit, delimiter)
    if info and getattr(info, "text_body", None):
        return json.loads(info.text_body).get("items", [])
    if ret:
        return ret.get("items", [])
    return []
