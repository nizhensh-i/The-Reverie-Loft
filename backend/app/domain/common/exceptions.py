"""
Domain/service layer exception exports.
Reuse root exceptions from app.exceptions to keep a single hierarchy.
"""

from ...exceptions import AppError as DomainError
from ...exceptions import NotFoundError
from ...exceptions import PermissionDeniedError as ForbiddenError
from ...exceptions import ValidationError

__all__ = ["DomainError", "ValidationError", "ForbiddenError", "NotFoundError"]
