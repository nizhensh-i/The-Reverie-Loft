from .service import (
    del_qiniu_image,
    detect_qiniu_capability,
    dir_file_name,
    generate_upload_token,
    get_random_user_avatars,
    get_signed_image_urls,
    setup_storage,
)

__all__ = [
    "setup_storage",
    "detect_qiniu_capability",
    "del_qiniu_image",
    "dir_file_name",
    "generate_upload_token",
    "get_random_user_avatars",
    "get_signed_image_urls",
]
