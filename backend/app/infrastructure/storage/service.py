import logging
import os
import random
import time

from ..capabilities import capability_enabled, get_capability, set_capability
from . import sdk

"""传/删图/签名/列举全部按 capability 降级（不可用时返回 None / [] / no-op）"""

QINIU_ENV_KEYS = (
    "QINIU_ACCESS_KEY",
    "QINIU_SECRET_KEY",
    "QINIU_BUCKET_NAME",
    "QINIU_DOMAIN",
)


def _qiniu_configured() -> tuple[bool, str]:
    missing = [key for key in QINIU_ENV_KEYS if not os.getenv(key)]
    if missing:
        return False, f"missing env config: {','.join(missing)}"
    return True, ""


def detect_qiniu_capability(force: bool = False) -> dict:
    if not force:
        existing = get_capability("storage_qiniu")
        if existing:
            return existing

    configured, reason = _qiniu_configured()
    if not configured:
        set_capability("storage_qiniu", enabled=False, degraded=True, reason=reason)
        return {"enabled": False, "degraded": True, "reason": reason}

    try:
        bucket = os.getenv("QINIU_BUCKET_NAME")
        # 轻量探测：列举1条，验证鉴权/网络/桶可访问性。
        sdk.list_items(bucket, prefix="", limit=1)
        set_capability("storage_qiniu", enabled=True, degraded=False, reason="")
        return {"enabled": True, "degraded": False, "reason": ""}
    except Exception as exc:
        reason = f"qiniu probe failed: {exc}"
        set_capability("storage_qiniu", enabled=False, degraded=True, reason=reason)
        return {"enabled": False, "degraded": True, "reason": reason}


def setup_storage(app=None):
    status = detect_qiniu_capability(force=True)
    if not status["enabled"]:
        logging.warning("七牛云存储降级: %s", status["reason"])


def _qiniu_available() -> bool:
    if capability_enabled("storage_qiniu", default=False):
        return True
    status = detect_qiniu_capability(force=False)
    return bool(status.get("enabled"))


def _resolve_bucket_name(bucket_name):
    return bucket_name or os.getenv("QINIU_BUCKET_NAME")


def _resolve_domain(domain):
    return domain or os.getenv("QINIU_DOMAIN") or ""


def _default_policy():
    return {
        "fsizeLimit": 10 * 1024 * 1024,
        "deadline": int(time.time()) + 3600,
    }


def generate_upload_token(policy=None, bucket_name=None):
    """生成token"""
    if not _qiniu_available():
        return None
    policy = policy or _default_policy()
    try:
        return sdk.build_upload_token(_resolve_bucket_name(bucket_name), policy=policy)
    except Exception as exc:
        logging.warning("生成七牛上传凭证失败: %s", exc)
        return None


def get_signed_image_urls(
    keys, domain=None, fops="imageMogr2/quality/80", expires=3600
):
    """生成私有存储图片url"""
    if not keys or not _qiniu_available():
        return []
    use_domain = _resolve_domain(domain)
    signed_urls = []
    for key in keys:
        base_url = f"{use_domain}/{key}"
        processed_url = base_url + "?" + fops
        try:
            private_url = sdk.build_private_download_url(processed_url, expires=expires)
            signed_urls.append(private_url)
        except Exception as exc:
            logging.warning("生成签名地址失败 key=%s err=%s", key, exc)
    return signed_urls


def del_qiniu_image(keys, bucket_name=None):
    """删除图片"""
    if not keys or not _qiniu_available():
        return
    try:
        return sdk.batch_delete(_resolve_bucket_name(bucket_name), keys)
    except Exception as exc:
        logging.warning("删除七牛图片失败 keys=%s err=%s", len(keys), exc)
        return None


def _list_items(prefix, bucket_name, limit=50, marker=None, delimiter=None):
    if not _qiniu_available():
        return []
    try:
        return sdk.list_items(
            _resolve_bucket_name(bucket_name),
            prefix=prefix,
            limit=limit,
            marker=marker,
            delimiter=delimiter,
        )
    except Exception as e:
        logging.warning(f"解析七牛云列表返回失败: {e}")
        return []


def _build_public_url(key, domain=None):
    if not key or key.startswith("http"):
        return key
    return f"{_resolve_domain(domain)}/{key}"


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
