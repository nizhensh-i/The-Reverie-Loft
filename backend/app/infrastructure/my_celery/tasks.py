import logging
import os

from celery import shared_task
from flask import render_template
from flask_mail import Message

from .. import db, mail


@shared_task(ignore_result=True)
def send_email(to, subject, template, **kwargs):
    try:
        message = Message(subject=subject, recipients=[to])
        message.html = render_template(template, **kwargs)
        mail.send(message)
    except Exception as e:
        print(e)
        print("发送失败")


@shared_task(ignore_result=True)
def hard_delete_post():
    """定期删除文章
    相关的评论、点赞、通知已通过 数据库级联 删除
    """
    try:
        from ...models import Post

        posts_query = Post.query.filter_by(deleted=True)
        post_count = posts_query.count()

        if post_count == 0:
            logging.info("Celery: 没有需要删除的文章")
            return

        post_ids = [p.id for p in posts_query.with_entities(Post.id).all()]
        logging.info(f"Celery: 开始删除文章，共 {post_count} 篇")

        # 删除相关图片
        image_count = _delete_post_images(post_ids)

        # 删除文章
        post_delete_result = posts_query.delete(synchronize_session=False)
        db.session.commit()

        logging.info(f"Celery: 批量删除完成，文章 {post_delete_result} 篇, 图片 {image_count} 张")

    except Exception as e:
        _handle_delete_error(e)


def _delete_post_images(post_ids):
    """删除文章相关图片"""
    from ...models import Image, ImageType

    images = (
        Image.query.with_entities(Image.id, Image.url)
        .filter(Image.type == ImageType.POST, Image.related_id.in_(post_ids))
        .all()
    )

    if not images:
        return 0

    image_ids, image_urls = zip(*images)

    # 删除七牛云图片
    _delete_qiniu_images(list(image_urls))

    # 删除数据库图片记录
    image_count = Image.query.filter(Image.id.in_(image_ids)).delete(
        synchronize_session=False
    )
    logging.info(f"数据库图片记录删除成功，共 {image_count} 条")

    return image_count


def _delete_qiniu_images(image_urls):
    """批量删除七牛云图片"""
    data = {
        "bucket_name": os.getenv("QINIU_BUCKET_NAME", ""),
        "keys": image_urls,
    }
    from ..storage.qiniu import del_qiniu_image

    del_qiniu_image(**data)
    logging.info(f"七牛云批量删除图片成功，共 {len(image_urls)} 张")


def _handle_delete_error(e):
    """处理删除过程中的错误"""
    error_msg = f"批量删除文章失败: {str(e)}"
    logging.error(error_msg, exc_info=True)
    db.session.rollback()

    try:
        from ...utils.time_util import DateUtils

        send_email.delay(
            "1912592745@qq.com",
            "Loft系统告警 - Celery批量删除文章失败",
            "error_email.html",
            username="admin",
            error_message=error_msg,
            year=DateUtils.get_year(),
        )
    except Exception as email_error:
        logging.error(f"发送错误邮件失败: {str(email_error)}", exc_info=True)
