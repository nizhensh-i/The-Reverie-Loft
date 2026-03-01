import logging

from ..application.dto import ActionResult, ItemResult
from ..domain.admin.policies import normalize_admin_post_type
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.text.markdown_truncate import MarkdownTruncator


class AdminPostService:
    def __init__(self, *, uow: UnitOfWork):
        self.uow = uow

    def rollback(self):
        self.uow.rollback()

    def init_post_summaries(self):
        posts_without_summary = self.uow.posts.list_posts_without_summary()
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
        posts_to_update_content = self.uow.posts.list_posts_without_content()
        for post in posts_to_update_content:
            post.content = post.body if post.body else ""
        if posts_to_update_content:
            self.uow.commit()

        post_ids_with_images = self.uow.posts.list_post_ids_with_images()
        if post_ids_with_images:
            self.uow.posts.bulk_mark_posts_has_image(post_ids_with_images)
            self.uow.commit()

        return ItemResult(
            data={
                "content_updated_count": len(posts_to_update_content),
                "post_ids_with_images_count": len(post_ids_with_images),
                "total_posts": self.uow.posts.count_posts(),
                "posts_with_has_image_true": self.uow.posts.count_posts_has_image(),
                "posts_with_content": self.uow.posts.count_posts_with_content(),
            }
        )

    def update_post_type(self, *, post_id: int, post_type: str):
        post = self.uow.posts.get_by_id(post_id)
        if not post:
            raise NotFoundError("文章不存在")
        normalized_type = normalize_admin_post_type(post_type)
        self.uow.posts.set_post_type(post, post_type_value=normalized_type.value)
        self.uow.commit()
        return ActionResult(
            message=f"成功为 id为{post_id} 的文章类型改为{post_type}",
            data={"post_id": post_id, "post_type": post_type},
        )
