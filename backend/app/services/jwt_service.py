from flask_jwt_extended import create_access_token, get_jwt


class JwtService:
    def __init__(self, redis_blocklist):
        self.redis_blocklist = redis_blocklist

    def refresh_access_token(self, *, user):
        return "Bearer " + create_access_token(identity=user)

    def revoke_current_token(self, *, expires_seconds: int):
        token = get_jwt()
        jti = token["jti"]
        token_type = token["type"]
        self.redis_blocklist.set(jti, "", ex=expires_seconds)
        return token_type

    @staticmethod
    def is_fresh_token():
        jwt_data = get_jwt()
        return bool(jwt_data.get("fresh", False))
