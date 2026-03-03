from __future__ import annotations

from datetime import timedelta
from typing import Any

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
)

from ...domain.ports.jwt import JwtPort


class FlaskJwtAdapter(JwtPort):
    @staticmethod
    def create_access_token(
        *,
        identity: Any,
        fresh: bool = False,
        expires_delta: timedelta | None = None,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        return create_access_token(
            identity=identity,
            fresh=fresh,
            expires_delta=expires_delta,
            additional_claims=additional_claims,
        )

    @staticmethod
    def create_refresh_token(*, identity: Any) -> str:
        return create_refresh_token(identity=identity)

    @staticmethod
    def decode_token(token: str, *, allow_expired: bool = False) -> dict[str, Any]:
        return decode_token(token, allow_expired=allow_expired)

    @staticmethod
    def get_jwt() -> dict[str, Any]:
        return get_jwt()
