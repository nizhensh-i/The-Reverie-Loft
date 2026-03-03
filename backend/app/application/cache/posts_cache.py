from __future__ import annotations

from ...domain.ports.cache import CachePort

POST_LIST_VERSION_KEY = "cache:posts:list:version"
POST_LIST_TIMEOUT_SECONDS = 60


class PostListCache:
    def __init__(self, *, cache: CachePort):
        self.cache = cache

    def _get_version(self) -> int:
        raw = self.cache.get(POST_LIST_VERSION_KEY)
        if raw is None:
            self.cache.set(POST_LIST_VERSION_KEY, 1)
            return 1
        try:
            return int(raw)
        except (TypeError, ValueError):
            self.cache.set(POST_LIST_VERSION_KEY, 1)
            return 1

    def _build_key(
        self, *, page: int, per_page: int, tab_name: str | None, viewer_id: int | None
    ) -> str:
        version = self._get_version()
        scope = tab_name or "all"
        owner = viewer_id or 0
        return f"cache:posts:list:v{version}:p{page}:pp{per_page}:t{scope}:u{owner}"

    def get(
        self, *, page: int, per_page: int, tab_name: str | None, viewer_id: int | None
    ):
        return self.cache.get(
            self._build_key(
                page=page,
                per_page=per_page,
                tab_name=tab_name,
                viewer_id=viewer_id,
            )
        )

    def set(
        self,
        *,
        page: int,
        per_page: int,
        tab_name: str | None,
        viewer_id: int | None,
        payload,
        timeout: int = POST_LIST_TIMEOUT_SECONDS,
    ) -> None:
        self.cache.set(
            self._build_key(
                page=page,
                per_page=per_page,
                tab_name=tab_name,
                viewer_id=viewer_id,
            ),
            payload,
            timeout=timeout,
        )

    def invalidate_all(self) -> None:
        current = self._get_version()
        self.cache.set(POST_LIST_VERSION_KEY, current + 1)
