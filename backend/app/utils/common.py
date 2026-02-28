import os


def get_avatars_url(key):
    if not key or key.startswith("http"):
        return key
    return f"{os.getenv('QINIU_DOMAIN')}/{key}-slim"
