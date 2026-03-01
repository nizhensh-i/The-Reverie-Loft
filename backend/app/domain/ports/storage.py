from __future__ import annotations

from typing import Protocol


class AvatarProviderPort(Protocol):
    def get_random_avatar(self) -> str:
        ...


class StoragePort(Protocol):
    def generate_upload_token(self, policy=None, bucket_name=None):
        ...

    def get_signed_image_urls(
        self,
        keys,
        *,
        domain=None,
        fops: str = "imageMogr2/quality/80",
        expires: int = 3600,
    ) -> list[str]:
        ...

    def delete_images(self, keys, bucket_name=None):
        ...

    def list_dir_files(
        self,
        *,
        prefix: str,
        current_page: int,
        page_size: int,
        complete_url: bool,
        bucket_name: str | None,
        url_builder=None,
    ):
        ...
