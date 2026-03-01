from __future__ import annotations

from ...infrastructure.cache import cache

POST_LIST_VERSION_KEY = "cache:posts:list:version"
POST_LIST_TIMEOUT_SECONDS = 60


class PostListCache:
    @staticmethod
    def _get_version() -> int:
        raw = cache.get(POST_LIST_VERSION_KEY)
        if raw is None:
            cache.set(POST_LIST_VERSION_KEY, 1)
            return 1
        try:
            return int(raw)
        except (TypeError, ValueError):
            cache.set(POST_LIST_VERSION_KEY, 1)
            return 1

    @classmethod
    def build_key(
        cls, *, page: int, per_page: int, tab_name: str | None, viewer_id: int | None
    ) -> str:
        version = cls._get_version()
        scope = tab_name or "all"
        owner = viewer_id or 0
        return f"cache:posts:list:v{version}:p{page}:pp{per_page}:t{scope}:u{owner}"

    @classmethod
    def get(
        cls, *, page: int, per_page: int, tab_name: str | None, viewer_id: int | None
    ):
        return cache.get(
            cls.build_key(
                page=page,
                per_page=per_page,
                tab_name=tab_name,
                viewer_id=viewer_id,
            )
        )

    @classmethod
    def set(
        cls,
        *,
        page: int,
        per_page: int,
        tab_name: str | None,
        viewer_id: int | None,
        payload,
        timeout: int = POST_LIST_TIMEOUT_SECONDS,
    ) -> None:
        cache.set(
            cls.build_key(
                page=page,
                per_page=per_page,
                tab_name=tab_name,
                viewer_id=viewer_id,
            ),
            payload,
            timeout=timeout,
        )

    @classmethod
    def invalidate_all(cls) -> None:
        current = cls._get_version()
        cache.set(POST_LIST_VERSION_KEY, current + 1)
