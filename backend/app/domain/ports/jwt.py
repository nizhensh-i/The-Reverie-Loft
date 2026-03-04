from __future__ import annotations

from datetime import timedelta
from typing import Any, Protocol


class JwtPort(Protocol):
    def create_access_token(
        self,
        *,
        identity: Any,
        fresh: bool = False,
        expires_delta: timedelta | None = None,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        ...

    def create_refresh_token(self, *, identity: Any) -> str:
        ...

    def decode_token(
        self, token: str, *, allow_expired: bool = False
    ) -> dict[str, Any]:
        ...

    def get_jwt(self) -> dict[str, Any]:
        ...
