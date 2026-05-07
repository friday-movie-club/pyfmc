"""Base resource class shared by all API resource modules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

if TYPE_CHECKING:
    from .client import FMCClient


class Resource:
    """Base class for API resource groups."""

    def __init__(self, client: FMCClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        resp = self._client._request(method, path, **kwargs)
        self._raise_for_status(resp)
        return resp

    def _get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def _patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("PATCH", path, **kwargs)

    def _put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            body = response.json()
            err = body.get("error", {})
            code = err.get("code", "UNKNOWN")
            message = err.get("message", response.text)
            details = err.get("details")
        except Exception:
            code = "UNKNOWN"
            message = response.text
            details = None

        status = response.status_code
        if status == 401:
            raise AuthenticationError(status, code, message)
        if status == 403:
            raise ForbiddenError(status, code, message)
        if status == 404:
            raise NotFoundError(status, code, message)
        if status == 409:
            raise ConflictError(status, code, message)
        if status == 422:
            raise ValidationError(status, code, message, details)
        raise APIError(status, code, message)
