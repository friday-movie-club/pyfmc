"""Auth API resource."""

from __future__ import annotations

from ._resource import Resource
from .models import AuthResponse, TokenPair


class AuthResource(Resource):
    """Endpoints under /auth."""

    def register(self, email: str, password: str, name: str) -> AuthResponse:
        """Register a new user account."""
        resp = self._post("/auth/register", json={"email": email, "password": password, "name": name})
        return AuthResponse.model_validate(resp.json())

    def resend_verification(self):
        """Resend the email verification."""
        self._post("/auth/resend-verification")

    def login(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ):
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
        response = AuthResponse.model_validate(resp.json())
        self._client.set_token(response.tokens.access_token)

    def refresh(self, refresh_token: str) -> TokenPair:
        """Exchange a refresh token for a new token pair."""
        resp = self._post("/auth/refresh", json={"refresh_token": refresh_token})
        return TokenPair.model_validate(resp.json())

    def verify_email(self, verification_token: str):
        """Verify a user's email address."""
        resp = self._post("/auth/verify-email", json={"token": verification_token})
