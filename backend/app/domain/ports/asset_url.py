from __future__ import annotations

from typing import Protocol


class AssetUrlPort(Protocol):
    def build(self, key: str | None) -> str | None:
        ...
