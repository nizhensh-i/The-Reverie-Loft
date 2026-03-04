"""Domain exceptions and shared error contracts."""


class DomainError(Exception):
    default_code = 500
    default_message = "Domain error"

    def __init__(self, message: str | None = None, code: int | None = None):
        self.message = message or self.default_message
        self.code = self.default_code if code is None else code
        super().__init__(self.message)


class ValidationError(DomainError, ValueError):
    default_code = 400
    default_message = "Validation failed"


class ForbiddenError(DomainError):
    default_code = 403
    default_message = "Forbidden"


class NotFoundError(DomainError):
    default_code = 404
    default_message = "Not found"


__all__ = ["DomainError", "ValidationError", "ForbiddenError", "NotFoundError"]
