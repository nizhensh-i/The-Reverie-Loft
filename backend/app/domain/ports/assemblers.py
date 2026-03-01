from __future__ import annotations

from typing import Any, Protocol


class ResponseAssemblerPort(Protocol):
    def batch_map_posts(
        self,
        posts,
        *,
        extra_data_map: dict[int, dict],
        is_list: bool = False,
    ) -> list[dict]:
        ...

    def map_user(self, user, *, extra_data: dict[str, Any]) -> dict[str, Any]:
        ...

    def map_comment(self, comment) -> dict[str, Any]:
        ...

    def map_created_comment(self, comment) -> dict[str, Any]:
        ...

    def map_admin_comment(self, comment) -> dict[str, Any]:
        ...

    def map_notification(self, notification) -> dict[str, Any]:
        ...

    def map_message(self, message) -> dict[str, Any]:
        ...

    def map_log(self, log) -> dict[str, Any]:
        ...

    def map_online_user(self, user) -> dict[str, Any]:
        ...

    def map_image(self, image) -> dict[str, Any]:
        ...
