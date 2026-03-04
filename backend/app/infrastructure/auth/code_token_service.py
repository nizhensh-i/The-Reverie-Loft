import random
import time
from datetime import timedelta
from typing import Optional

from flask_jwt_extended import create_access_token


class AuthCodeTokenService:
    def __init__(self, redis_client):
        self.redis = redis_client
        # Redis 不可用时的进程内降级存储：email -> (code, expire_ts)
        self._fallback_codes = {}

    def generate_email_code(
        self, email: str, expiration: int = 60 * 3
    ) -> Optional[int]:
        code = random.randint(100000, 999999)
        try:
            self.redis.setex(email, expiration, code)
        except Exception:
            self._fallback_codes[email] = (str(code), int(time.time()) + expiration)
        return code

    def compare_email_code(self, email: str, code: str | int) -> bool:
        try:
            stored = self.redis.get(email)
        except Exception:
            stored = None

        if stored:
            return str(code) == str(stored)

        fallback = self._fallback_codes.get(email)
        if not fallback:
            return False

        stored_code, expire_ts = fallback
        if int(time.time()) > expire_ts:
            self._fallback_codes.pop(email, None)
            return False
        return str(code) == stored_code

    def clear_email_code(self, email: str):
        try:
            self.redis.delete(email)
        except Exception:
            pass
        self._fallback_codes.pop(email, None)

    @staticmethod
    def generate_confirmation_token(identity, user_id: int, expiration: int = 3600):
        additional_claims = {"confirm": user_id}
        return create_access_token(
            identity=identity,
            additional_claims=additional_claims,
            expires_delta=timedelta(seconds=expiration),
        )
