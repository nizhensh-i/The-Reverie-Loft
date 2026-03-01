from __future__ import annotations

from typing import Protocol


class OAuthNetworkPort(Protocol):
    def has_network_error_message(self, message: str) -> bool:
        ...
