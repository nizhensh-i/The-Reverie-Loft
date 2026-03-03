from __future__ import annotations

from typing import Any, Protocol


class CachePort(Protocol):
    def get(self, key: str) -> Any:
        ...

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        ...
