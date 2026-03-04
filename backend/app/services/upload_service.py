import os
import time

from ..application.dto import ActionResult, ItemResult, ListResult, PageResult
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.asset_url import AssetUrlPort
from ..domain.ports.storage import StoragePort
from ..domain.upload.policies import (
    build_upload_token_policy,
    resolve_interest_image_type,
)


class UploadService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        storage: StoragePort,
        assembler: ResponseAssemblerPort,
        asset_url: AssetUrlPort,
    ):
        self.uow = uow
        self.storage = storage
        self.assembler = assembler
        self.asset_url = asset_url

    def rollback(self):
        self.uow.rollback()

    def create_upload_token(self):
        policy = build_upload_token_policy(now_ts=int(time.time()))
        token = self.storage.generate_upload_token(policy=policy)
        return ItemResult(data={"upload_token": token})

    def list_signed_image_urls(self, *, keys):
        signed_urls = self.storage.get_signed_image_urls(
            keys,
            domain=os.getenv("QINIU_DOMAIN"),
            fops="imageMogr2/quality/80",
            expires=3600,
        )
        return ListResult(data=signed_urls)

    def delete_images(self, *, keys, bucket_name=None):
        self.storage.delete_images(keys, bucket_name)
        return ActionResult(message="图片删除成功")

    def list_dir_files(
        self,
        *,
        prefix: str,
        current_page: int,
        page_size: int,
        complete_url: bool,
        bucket_name: str,
    ):
        data, total = self.storage.list_dir_files(
            prefix=prefix,
            current_page=current_page,
            page_size=page_size,
            complete_url=complete_url,
            bucket_name=bucket_name,
            url_builder=self.asset_url.build if complete_url else None,
        )
        return PageResult(data=data, total=total)

    def update_interest_images(self, *, user_id: int, urls, names, interest_type: str):
        type_code = resolve_interest_image_type(interest_type)
        image_type_code = type_code.value

        last_upload_images = self.uow.uploads.list_interest_images(
            user_id=user_id, image_type=image_type_code
        )
        if last_upload_images:
            image_keys = [image.url for image in last_upload_images]
            self.storage.delete_images(image_keys)
            for item in last_upload_images:
                self.uow.uploads.delete(item)
            self.uow.commit()

        images = self.uow.uploads.create_interest_images(
            user_id=user_id,
            interest_type_code=image_type_code,
            urls=urls,
            names=names,
        )
        if images:
            self.uow.uploads.add_all(images)
            self.uow.commit()
        return ListResult(data=[self.assembler.map_image(image) for image in images])
