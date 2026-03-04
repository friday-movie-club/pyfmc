"""Auth API resource."""

from __future__ import annotations

from ._resource import Resource
from .models import AuthResponse, SocialLoginURL, TokenPair


class AuthResource(Resource):
    """Endpoints under /auth."""

    def register(self, email: str, password: str, name: str) -> AuthResponse:
        """Register a new user account."""
        resp = self._post("/auth/register", json={"email": email, "password": password, "name": name})
        self._raise_for_status(resp)
        return AuthResponse.model_validate(resp.json())

    def login(self, *, email: str | None = None, password: str | None = None, token: str | None = None) -> AuthResponse:
        """Login with email/password or a Personal Access Token.

        Pass ``token`` for PAT login, or ``email`` + ``password`` for standard login.
        """
        if token is not None:
            body: dict = {"token": token}
        else:
            if email is None or password is None:
                raise ValueError("Provide either 'token' or both 'email' and 'password'")
            body = {"email": email, "password": password}
        resp = self._post("/auth/login", json=body)
        self._raise_for_status(resp)
        return AuthResponse.model_validate(resp.json())

    def refresh(self, refresh_token: str) -> TokenPair:
        """Exchange a refresh token for a new token pair."""
        resp = self._post("/auth/refresh", json={"refresh_token": refresh_token})
        self._raise_for_status(resp)
        return TokenPair.model_validate(resp.json())

    def exchange(self, code: str) -> AuthResponse:
        """Exchange an OAuth authorization code for tokens."""
        resp = self._post("/auth/exchange", json={"code": code})
        self._raise_for_status(resp)
        return AuthResponse.model_validate(resp.json())

    def social_register(self, social_token: str, name: str) -> AuthResponse:
        """Complete social-auth registration for a new user."""
        resp = self._post("/auth/social/register", json={"social_token": social_token, "name": name})
        self._raise_for_status(resp)
        return AuthResponse.model_validate(resp.json())

    def social_login_url(self, provider: str) -> SocialLoginURL:
        """Get the OAuth login URL for *provider* (``"google"`` or ``"apple"``)."""
        resp = self._get(f"/auth/{provider}/login")
        self._raise_for_status(resp)
        return SocialLoginURL.model_validate(resp.json())
