from __future__ import annotations

from typing import Protocol


class PresencePort(Protocol):
    def list_online_user_ids(self) -> set[int]:
        ...
