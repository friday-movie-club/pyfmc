"""Users API resource."""

from __future__ import annotations

from uuid import UUID

from ._resource import Resource
from .models import PaginatedResult, User, UserToken


class UsersResource(Resource):
    """Endpoints under /users/me."""

    def me(self) -> User:
        """Get the current authenticated user's profile."""
        resp = self._get("/users/me")
        return User.model_validate(resp.json())

    def update_me(self, *, name: str | None = None, avatar_url: str | None = None) -> User:
        """Update the current user's profile."""
        body = {}
        if name is not None:
            body["name"] = name
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        resp = self._patch("/users/me", json=body)
        return User.model_validate(resp.json())

    def delete_me(self) -> None:
        """Permanently delete the current user's account."""
        resp = self._delete("/users/me")

    def create_token(self, name: str) -> dict:
        """Create a Personal Access Token.

        Returns a dict with ``token`` (the :class:`UserToken`) and
        ``raw_token`` (the plaintext token string — store it safely).
        """
        resp = self._post("/users/me/tokens", json={"name": name})
        data = resp.json()
        return {
            "token": UserToken.model_validate(data["token"]),
            "raw_token": data["raw_token"],
        }

    def list_tokens(self) -> PaginatedResult[UserToken]:
        """List all Personal Access Tokens for the current user."""
        resp = self._get("/users/me/tokens")
        data = resp.json()
        return PaginatedResult[UserToken](
            items=[UserToken.model_validate(t) for t in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def delete_token(self, token_id: UUID | str) -> None:
        """Delete a Personal Access Token by its ID."""
        resp = self._delete(f"/users/me/tokens/{token_id}")
