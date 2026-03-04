from __future__ import annotations

from typing import Protocol


class PaginationSettingsPort(Protocol):
    def posts_per_page(self) -> int:
        ...

    def followers_per_page(self) -> int:
        ...

    def chat_per_page(self) -> int:
        ...
