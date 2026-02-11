import logging
from functools import wraps

from flask_caching import Cache

cache = Cache()


def setup_cache(app):
    cache.init_app(app)


def invalidate_post_cache():
    """
    清除文章相关的缓存
    在发布文章，评论、点赞等操作后调用，确保缓存一致性

    """

    try:
        # 使用延迟导入避免循环引用
        from ...api.posts import PostGroupApi

        cache.delete_memoized(PostGroupApi.query_post)
        logging.debug("文章缓存已清除")
    except Exception as e:
        logging.error(f"清除缓存失败: {str(e)}", exc_info=True)


def cache_invalidator(f):
    """
    缓存清除装饰器
    装饰的函数执行后会自动清除文章缓存
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            # 函数执行成功后清除缓存
            invalidate_post_cache()
            return result
        except Exception as e:
            # 函数执行失败仍然记录错误，但不阻止异常抛出
            logging.error(f"函数执行失败: {str(e)}", exc_info=True)
            raise

    return wrapper
