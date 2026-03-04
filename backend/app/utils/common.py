import os


def get_avatars_url(key):
    if not key or key.startswith("http"):
        return key
    if key.startswith("local_avatar:"):
        filename = key.split(":", 1)[1]
        return f"/avatars/{filename}"
    if key.startswith("/"):
        return key
    return f"{os.getenv('QINIU_DOMAIN')}/{key}-slim"
