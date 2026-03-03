from ..application.dto import ActionResult, ItemResult
from ..domain.ports.jwt import JwtPort


class JwtService:
    def __init__(self, *, redis_blocklist, jwt_port: JwtPort):
        self.redis_blocklist = redis_blocklist
        self.jwt_port = jwt_port

    def refresh_access_token(self, *, user):
        return ItemResult(
            data={
                "access_token": "Bearer "
                + self.jwt_port.create_access_token(identity=user)
            }
        )

    def revoke_current_token(self, *, expires_seconds: int):
        token = self.jwt_port.get_jwt()
        jti = token["jti"]
        token_type = token["type"]
        self.redis_blocklist.set(jti, "", ex=expires_seconds)
        return ActionResult(
            message=f"{token_type.capitalize()} token successfully revoked",
            data={"token_type": token_type},
        )

    def is_fresh_token(self):
        jwt_data = self.jwt_port.get_jwt()
        return ItemResult(data={"is_fresh": bool(jwt_data.get("fresh", False))})
