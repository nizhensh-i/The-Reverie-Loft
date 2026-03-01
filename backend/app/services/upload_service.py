import os
import time

from sqlalchemy import and_

from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.storage import (
    del_qiniu_image,
    dir_file_name,
    generate_upload_token,
)
from ..infrastructure.storage import get_signed_image_urls as build_signed_image_urls
from ..models import Image, ImageType
from ..utils.common import get_avatars_url
from .common.dto import ActionResult, ItemResult, ListResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class UploadService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def create_upload_token(self):
        policy = {
            "fsizeLimit": 10 * 1024 * 1024,
            "deadline": int(time.time()) + 3600,
        }
        token = generate_upload_token(policy=policy)
        return ItemResult(data={"upload_token": token})

    def list_signed_image_urls(self, *, keys):
        signed_urls = build_signed_image_urls(
            keys,
            domain=os.getenv("QINIU_DOMAIN"),
            fops="imageMogr2/quality/80",
            expires=3600,
        )
        return ListResult(data=signed_urls)

    def delete_images(self, *, keys, bucket_name=None):
        del_qiniu_image(keys, bucket_name)
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
        data, total = dir_file_name(
            prefix,
            current_page,
            page_size,
            complete_url,
            bucket_name,
            url_builder=get_avatars_url if complete_url else None,
        )
        return PageResult(data=data, total=total)

    def update_interest_images(self, *, user_id: int, urls, names, interest_type: str):
        type_url = None
        if interest_type == "movie":
            type_url = ImageType.MOVIE
        elif interest_type == "book":
            type_url = ImageType.BOOK

        last_upload_images = Image.query.filter(
            and_(Image.type == type_url, Image.related_id == user_id)
        ).all()
        if last_upload_images:
            image_keys = [image.url for image in last_upload_images]
            del_qiniu_image(image_keys)
            for item in last_upload_images:
                self.session.delete(item)
            self.uow.commit()

        images = [
            Image(url=url, type=type_url, describe=name, related_id=user_id)
            for url, name in zip(urls, names)
        ]
        if images:
            self.session.add_all(images)
            self.uow.commit()
        return ListResult(data=[image.to_json() for image in images])
