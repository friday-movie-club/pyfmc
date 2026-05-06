"""Main FMCClient class."""

from __future__ import annotations

from typing import Any

import httpx

from .auth import AuthResource
from .clubs import ClubsResource
from .events import EventsResource
from .movies import MoviesResource
from .subscriptions import SubscriptionsResource
from .users import UsersResource

_DEFAULT_BASE_URL = "http://localhost:8080/api/v1"


class FMCClient:
    """Synchronous HTTP client for the Friday Movie Club API.

    Usage::

        client = FMCClient(base_url="https://api.example.com/api/v1")

        # Register and get tokens
        auth_resp = client.auth.register("user@example.com", "password", "Alice")
        client.set_token(auth_resp.tokens.access_token)

        # Use the API
        clubs = client.clubs.list()

    All resource groups are available as attributes:

    * :attr:`auth`   – authentication and token management
    * :attr:`users`  – current-user profile and PATs
    * :attr:`clubs`  – club CRUD, members, and invitations
    * :attr:`movies` – suggestions, rankings, and TMDB search
    * :attr:`events` – event CRUD, RSVP, and movie assignment
    * :attr:`subscriptions` – subscription plans and user subscription
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        *,
        token: str | None = None,
        timeout: float = 30.0,
        verify: bool = True,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token: str | None = token
        self._http = httpx.Client(timeout=timeout, verify=verify)

        self.auth = AuthResource(self)
        self.users = UsersResource(self)
        self.clubs = ClubsResource(self)
        self.movies = MoviesResource(self)
        self.events = EventsResource(self)
        self.subscriptions = SubscriptionsResource(self)

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def set_token(self, access_token: str) -> None:
        """Set the Bearer token used for authenticated requests."""
        self._token = access_token

    def clear_token(self) -> None:
        """Remove the current Bearer token."""
        self._token = None

    # ------------------------------------------------------------------
    # Low-level request helper (used by Resource subclasses)
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        url = self._base_url + path
        headers = kwargs.pop("headers", {})
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return self._http.request(method, url, headers=headers, **kwargs)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> FMCClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()
