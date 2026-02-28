import logging
from functools import wraps
from typing import Callable, Optional

from flask_caching import Cache

from ..capabilities import capability_enabled, get_capability, set_capability
from ..exceptions import CacheError

cache = Cache()


def setup_cache(app):
    redis_up = capability_enabled("redis", default=True)
    if not redis_up:
        # Redis 缓存不可用时回退到进程内缓存，避免主流程受影响。
        app.config["CACHE_TYPE"] = "SimpleCache"
        app.config.setdefault("CACHE_DEFAULT_TIMEOUT", 300)
        reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
        set_capability(
            "cache",
            enabled=True,
            degraded=True,
            reason=f"fallback to SimpleCache: {reason}",
        )
    else:
        set_capability("cache", enabled=True, degraded=False, reason="")
    cache.init_app(app)


def invalidate_cache_by_key(key: str, raise_on_error: bool = False) -> bool:
    """
    根据缓存键清除缓存

    Args:
        key: 缓存键
        raise_on_error: 是否在出错时抛出异常

    Returns:
        bool: 是否成功清除
    """
    try:
        result = cache.delete(key)
        logging.debug(f"缓存已清除: {key}")
        return result
    except Exception as e:
        error_msg = f"清除缓存失败 (key: {key}): {str(e)}"
        logging.error(error_msg, exc_info=True)
        if raise_on_error:
            raise CacheError(error_msg, component="cache", original_error=e)
        return False


def invalidate_cache_by_pattern(pattern: str, raise_on_error: bool = False) -> int:
    """
    根据模式清除缓存（如果缓存后端支持）

    Args:
        pattern: 缓存键模式（如 'post_*'）
        raise_on_error: 是否在出错时抛出异常

    Returns:
        int: 清除的缓存数量
    """
    try:
        # Flask-Caching 的 delete_memoized 可以用于清除 memoized 函数缓存
        # 对于 Redis 缓存，可以使用 cache.clear() 或具体的键删除
        logging.warning(f"模式清除缓存可能不被所有后端支持: {pattern}")
        return 0
    except Exception as e:
        error_msg = f"模式清除缓存失败 (pattern: {pattern}): {str(e)}"
        logging.error(error_msg, exc_info=True)
        if raise_on_error:
            raise CacheError(error_msg, component="cache", original_error=e)
        return 0


def invalidate_memoized_function(
    func: Callable, raise_on_error: bool = False, *args, **kwargs
) -> bool:
    """
    清除 memoized 函数的缓存

    Args:
        func: 被 memoized 的函数
        raise_on_error: 是否在出错时抛出异常
        *args, **kwargs: 传递给 delete_memoized 的参数

    Returns:
        bool: 是否成功清除
    """
    try:
        cache.delete_memoized(func, *args, **kwargs)
        logging.debug(f"Memoized 函数缓存已清除: {func.__name__}")
        return True
    except Exception as e:
        error_msg = f"清除 memoized 函数缓存失败 ({func.__name__}): {str(e)}"
        logging.error(error_msg, exc_info=True)
        if raise_on_error:
            raise CacheError(error_msg, component="cache", original_error=e)
        return False


def create_cache_invalidator(
    target_key: Optional[str] = None, target_func: Optional[Callable] = None
) -> Callable:
    """
    创建缓存失效器工厂函数

    Args:
        target_key: 要清除的缓存键
        target_func: 要清除的 memoized 函数

    Returns:
        缓存失效器函数
    """

    def invalidate():
        if target_key:
            return invalidate_cache_by_key(target_key)
        elif target_func:
            return invalidate_memoized_function(target_func)
        else:
            logging.warning("未指定要清除的缓存目标")
            return False

    return invalidate


def cache_invalidator(
    target_key: Optional[str] = None,
    target_func: Optional[Callable] = None,
    raise_on_error: bool = False,
):
    """
    缓存清除装饰器 - 重构版本

    Args:
        target_key: 要清除的缓存键
        target_func: 要清除的 memoized 函数
        raise_on_error: 是否在清除缓存失败时抛出异常

    Returns:
        装饰器函数
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 先执行原函数
            result = f(*args, **kwargs)

            # 执行成功后清除缓存
            try:
                if target_key:
                    invalidate_cache_by_key(target_key, raise_on_error)
                elif target_func:
                    invalidate_memoized_function(target_func, raise_on_error)
            except Exception as e:
                # 缓存清除失败记录警告，但不影响主流程
                logging.warning(f"缓存清除失败，但不影响主流程: {str(e)}")

            return result

        return wrapper

    return decorator
