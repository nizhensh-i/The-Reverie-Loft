import logging

from ..infrastructure.database.sqlalchemy import db
from ..models import Image, ImageType, Post, PostType
from ..utils.markdown_truncate import MarkdownTruncator
from .common.dto import ActionResult, ItemResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class AdminPostService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def init_post_summaries(self):
        posts_without_summary = Post.query.filter(
            (Post.summary.is_(None)) | (Post.summary == "")
        ).all()
        total_posts = len(posts_without_summary)
        logging.info("找到 %s 篇需要初始化summary的文章", total_posts)
        if total_posts == 0:
            return ItemResult(data={"updated_count": 0, "total_found": 0})

        updated_count = 0
        for post in posts_without_summary:
            try:
                content = post.content or ""
                is_pure_text = post.derived_type != "markdown"
                if content:
                    summary = MarkdownTruncator.get_smart_preview(content, is_pure_text)
                    post.summary = summary
                    updated_count += 1
                    if updated_count % 100 == 0:
                        self.uow.commit()
                else:
                    logging.warning("文章ID %s 没有内容，跳过", post.id)
            except Exception as exc:
                logging.error("处理文章ID %s 时出错: %s", post.id, str(exc))
                continue

        self.uow.commit()
        return ItemResult(
            data={"updated_count": updated_count, "total_found": total_posts}
        )

    def migrate_post_content_and_has_image(self):
        posts_to_update_content = Post.query.filter(
            (Post.content.is_(None)) | (Post.content == "")
        ).all()
        for post in posts_to_update_content:
            post.content = post.body if post.body else ""
        if posts_to_update_content:
            self.uow.commit()

        posts_with_images = (
            self.session.query(Image.related_id)
            .filter(Image.type == ImageType.POST)
            .distinct()
            .all()
        )
        post_ids_with_images = [post_id for post_id, in posts_with_images]
        if post_ids_with_images:
            Post.query.filter(Post.id.in_(post_ids_with_images)).update(
                {Post.has_image: True}, synchronize_session=False
            )
            self.uow.commit()

        return ItemResult(
            data={
                "content_updated_count": len(posts_to_update_content),
                "post_ids_with_images_count": len(post_ids_with_images),
                "total_posts": Post.query.count(),
                "posts_with_has_image_true": Post.query.filter(
                    Post.has_image.is_(True)
                ).count(),
                "posts_with_content": Post.query.filter(
                    (Post.content.isnot(None)) & (Post.content != "")
                ).count(),
            }
        )

    def update_post_type(self, *, post_id: int, post_type: str):
        post = Post.query.filter_by(id=post_id).first()
        post.type = (
            PostType.TEXT if post_type == PostType.TEXT.value else PostType.MARKDOWN
        )
        self.uow.commit()
        return ActionResult(
            message=f"成功为 id为{post_id} 的文章类型改为{post_type}",
            data={"post_id": post_id, "post_type": post_type},
        )
