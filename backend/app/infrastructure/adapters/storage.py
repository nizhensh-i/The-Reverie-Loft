from ...domain.ports.storage import AvatarProviderPort, StoragePort
from ..storage import (
    del_qiniu_image,
    dir_file_name,
    generate_upload_token,
    get_random_user_avatars,
    get_signed_image_urls,
)


class QiniuAvatarProvider(AvatarProviderPort):
    @staticmethod
    def get_random_avatar() -> str:
        return get_random_user_avatars()


class QiniuStorageAdapter(StoragePort):
    @staticmethod
    def generate_upload_token(policy=None, bucket_name=None):
        return generate_upload_token(policy=policy, bucket_name=bucket_name)

    @staticmethod
    def get_signed_image_urls(
        keys,
        *,
        domain=None,
        fops: str = "imageMogr2/quality/80",
        expires: int = 3600,
    ) -> list[str]:
        return get_signed_image_urls(keys, domain=domain, fops=fops, expires=expires)

    @staticmethod
    def delete_images(keys, bucket_name=None):
        return del_qiniu_image(keys, bucket_name=bucket_name)

    @staticmethod
    def list_dir_files(
        *,
        prefix: str,
        current_page: int,
        page_size: int,
        complete_url: bool,
        bucket_name: str | None,
        url_builder=None,
    ):
        return dir_file_name(
            prefix,
            current_page,
            page_size,
            complete_url,
            bucket_name,
            url_builder=url_builder,
        )
