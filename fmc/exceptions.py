"""Exceptions raised by the fmc client."""

from __future__ import annotations


class FMCError(Exception):
    """Base exception for all fmc errors."""


class APIError(FMCError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"[{status_code}] {code}: {message}")


class AuthenticationError(APIError):
    """Raised on 401 Unauthorized responses."""


class ForbiddenError(APIError):
    """Raised on 403 Forbidden responses."""


class NotFoundError(APIError):
    """Raised on 404 Not Found responses."""


class ConflictError(APIError):
    """Raised on 409 Conflict responses."""


class ValidationError(APIError):
    """Raised on 422 Unprocessable Entity responses."""

    def __init__(self, status_code: int, code: str, message: str, details: object = None) -> None:
        self.details = details
        super().__init__(status_code, code, message)
