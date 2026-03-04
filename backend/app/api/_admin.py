import logging

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import jwt_required

from ..container import AppContainer
from ..decorators import permission_required
from ..domain.common.constants import PermissionCode
from ..services.admin_post_service import AdminPostService
from ..utils.response import error, success
from . import api


@inject
def _admin_post_service(
    admin_post_service: AdminPostService = Provide[AppContainer.admin_post_service],
) -> AdminPostService:
    return admin_post_service


@api.route("/admin/init-summaries", methods=["POST"])
@jwt_required()
@permission_required(PermissionCode.ADMIN)
def post_init_summary():
    try:
        result = _admin_post_service().init_post_summaries()
        updated_count = result.data["updated_count"]
        total_posts = result.data["total_found"]
        if total_posts == 0:
            return success(message="所有文章都已有summary，无需处理", data={"updated_count": 0})
        logging.info(f"成功为 {updated_count} 篇文章初始化了summary字段")

        return success(
            message=f"成功为 {updated_count} 篇文章初始化了summary字段",
            data={"updated_count": updated_count, "total_found": total_posts},
        )

    except Exception as e:
        logging.error(f"初始化summary字段时出错: {str(e)}")
        _admin_post_service().rollback()
        return error(500, f"初始化summary字段时出错: {str(e)}")


@api.route("/admin/modify-post", methods=["POST"])
@jwt_required()
@permission_required(PermissionCode.ADMIN)
def update_posts():
    try:
        result = _admin_post_service().migrate_post_content_and_has_image()
        logging.info(f"   找到 {result.data['content_updated_count']} 条需要更新content的记录")
    except Exception as e:
        _admin_post_service().rollback()
        logging.error("更新content字段出错", e)
        return error(500, f"更新content字段出错: {str(e)}")
    logging.info(f"   总文章数: {result.data['total_posts']}")
    logging.info(f"   有图片的文章数: {result.data['posts_with_has_image_true']}")
    logging.info(f"   有content内容的文章数: {result.data['posts_with_content']}")

    logging.info("\n✅ 数据迁移完成！")
    return success(
        message=f"成功为 {result.data['content_updated_count']} 篇文章初始化了content字段",
        data="",
    )


@api.route("/admin/modify-post-type", methods=["POST"])
@jwt_required()
@permission_required(PermissionCode.ADMIN)
def update_post_type():
    post_id = request.json.get("post_id")
    post_type = request.json.get("post_type")
    logging.info(f"文章id:{post_id}， 文章类型：{post_type}")
    try:
        result = _admin_post_service().update_post_type(
            post_id=post_id, post_type=post_type
        )
    except Exception as e:
        _admin_post_service().rollback()
        logging.error("更新文章类型字段出错", e)
        return error(500, f"更新文章类型字段出错: {str(e)}")

    return success(message=result.message, data=result.data)
