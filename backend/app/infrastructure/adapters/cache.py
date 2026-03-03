from __future__ import annotations

from typing import Any

from ...domain.ports.cache import CachePort


class FlaskCacheAdapter(CachePort):
    def __init__(self, cache_client):
        self.cache = cache_client

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        self.cache.set(key, value, timeout=timeout)
