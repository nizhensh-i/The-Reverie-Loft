import logging

from flask import request
from flask_jwt_extended import jwt_required

from ..decorators import permission_required
from ..infrastructure.database.sqlalchemy import db
from ..models import Image, ImageType, Permission, Post, PostType
from ..utils.markdown_truncate import MarkdownTruncator
from ..utils.response import error, success
from . import api


@api.route("/admin/init-summaries", methods=["POST"])
@jwt_required()
@permission_required(Permission.ADMIN)
def post_init_summary():
    """
    管理员专用：为所有现有文章初始化summary字段
    如果文章的summary为空，则使用get_smart_preview方法生成summary
    """
    try:
        # 查询所有summary为空的文章
        posts_without_summary = Post.query.filter(
            (Post.summary.is_(None)) | (Post.summary == "")
        ).all()
        # posts_without_summary = Post.query.all()

        total_posts = len(posts_without_summary)
        logging.info(f"找到 {total_posts} 篇需要初始化summary的文章")

        if total_posts == 0:
            return success(message="所有文章都已有summary，无需处理", data={"updated_count": 0})

        # 批量更新文章的summary
        updated_count = 0
        for post in posts_without_summary:
            try:
                # 使用content生成summary
                content = post.content or ""
                is_pure_text = post.derived_type != "markdown"
                if content:
                    summary = MarkdownTruncator.get_smart_preview(content, is_pure_text)
                    logging.info(f"summary长度: {len(summary)}")
                    post.summary = summary
                    updated_count += 1

                    # 每100篇提交一次，避免内存占用过大
                    if updated_count % 100 == 0:
                        db.session.commit()
                        logging.info(f"已处理 {updated_count}/{total_posts} 篇文章")
                else:
                    logging.warning(f"文章ID {post.id} 没有内容，跳过")

            except Exception as e:
                logging.error(f"处理文章ID {post.id} 时出错: {str(e)}")
                continue

        # 提交剩余的更改
        db.session.commit()
        logging.info(f"成功为 {updated_count} 篇文章初始化了summary字段")

        return success(
            message=f"成功为 {updated_count} 篇文章初始化了summary字段",
            data={"updated_count": updated_count, "total_found": total_posts},
        )

    except Exception as e:
        logging.error(f"初始化summary字段时出错: {str(e)}")
        db.session.rollback()
        return error(500, f"初始化summary字段时出错: {str(e)}")


@api.route("/admin/modify-post", methods=["POST"])
@jwt_required()
@permission_required(Permission.ADMIN)
def update_posts():
    """更新Post模型content, has_image字段数据"""

    # 1. 更新content字段：将body的值复制到content
    logging.info("\n1. 更新content字段...")
    try:
        posts_to_update_content = Post.query.filter(
            (Post.content.is_(None)) | (Post.content == "")
        ).all()

        logging.info(f"   找到 {len(posts_to_update_content)} 条需要更新content的记录")

        for post in posts_to_update_content:
            post.content = post.body if post.body else ""

        if posts_to_update_content:
            db.session.commit()
            logging.info("   ✓ content字段更新完成")
        else:
            logging.info("   ✓ 所有记录的content字段已存在，无需更新")
    except Exception as e:
        db.session.rollback()
        logging.error("更新content字段出错", e)
        return error(500, f"更新content字段出错: {str(e)}")

    # 2. 更新has_image字段：检查每篇文章是否有相关图片
    logging.info("\n2. 更新has_image字段...")

    try:
        # 获取所有有图片的文章ID
        posts_with_images = (
            db.session.query(Image.related_id)
            .filter(Image.type == ImageType.POST)
            .distinct()
            .all()
        )

        post_ids_with_images = [post_id for post_id, in posts_with_images]
        logging.info(f"   找到 {len(post_ids_with_images)} 篇有图片的文章")

        # 批量更新有图片的文章
        if post_ids_with_images:
            Post.query.filter(Post.id.in_(post_ids_with_images)).update(
                {Post.has_image: True}, synchronize_session=False
            )
            db.session.commit()
            logging.info("   ✓ has_image字段更新完成")
    except Exception as e:
        db.session.rollback()
        logging.error("更新has_image字段出错", e)
        return error(500, f"更新has_image字段出错: {str(e)}")

    # 3. 验证更新结果
    logging.info("\n3. 验证更新结果...")
    total_posts = Post.query.count()
    posts_with_has_image_true = Post.query.filter(Post.has_image.is_(True)).count()
    posts_with_content = Post.query.filter(
        (Post.content.isnot(None)) & (Post.content != "")
    ).count()

    logging.info(f"   总文章数: {total_posts}")
    logging.info(f"   有图片的文章数: {posts_with_has_image_true}")
    logging.info(f"   有content内容的文章数: {posts_with_content}")

    logging.info("\n✅ 数据迁移完成！")
    return success(
        message=f"成功为 {len(posts_to_update_content)} 篇文章初始化了content字段",
        data="",
    )


@api.route("/admin/modify-post-type", methods=["POST"])
@jwt_required()
@permission_required(Permission.ADMIN)
def update_post_type():
    """根据文章id更新文章类型"""
    post_id = request.json.get("post_id")
    post_type = request.json.get("post_type")
    logging.info(f"文章id:{post_id}， 文章类型：{post_type}")
    try:
        post = Post.query.filter_by(id=post_id).first()
        post.type = (
            PostType.TEXT if post_type == PostType.TEXT.value else PostType.MARKDOWN
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error("更新文章类型字段出错", e)
        return error(500, f"更新文章类型字段出错: {str(e)}")

    return success(
        message=f"成功为 id为{post_id} 的文章类型改为{post_type}",
        data="",
    )
