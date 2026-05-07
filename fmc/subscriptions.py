"""Subscriptions API resource."""

from __future__ import annotations

from uuid import UUID

from ._resource import Resource
from .models import PaginatedResult, SubscriptionPlan, UserSubscription


class SubscriptionsResource(Resource):
    """Endpoints for subscription plans and the current user's subscription."""

    def list_plans(self) -> PaginatedResult[SubscriptionPlan]:
        """List all available subscription plans (public endpoint)."""
        resp = self._get("/subscription-plans")
        data = resp.json()
        return PaginatedResult[SubscriptionPlan](
            items=[SubscriptionPlan.model_validate(p) for p in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def get(self) -> UserSubscription:
        """Get the current user's subscription."""
        resp = self._get("/users/me/subscription")
        return UserSubscription.model_validate(resp.json())

    def create(self, plan_id: UUID | str, promo_code: str | None = None) -> UserSubscription:
        """Create a subscription for the current user on the given plan."""
        body: dict = {"plan_id": str(plan_id)}
        if promo_code is not None:
            body["promo_code"] = promo_code
        resp = self._post("/users/me/subscription", json=body)
        return UserSubscription.model_validate(resp.json())

    def cancel(self) -> None:
        """Cancel the current user's subscription."""
        resp = self._patch("/users/me/subscription", json={"action": "cancel"})

    def apply_promo_code(self, code: str) -> UserSubscription:
        """Apply a promo code to the current user's subscription."""
        resp = self._post("/users/me/promo-code", json={"code": code})
        return UserSubscription.model_validate(resp.json())

    def customer_portal_url(self, return_url: str | None = None) -> str:
        """Get a Stripe customer-portal URL for the current user."""
        params: dict = {}
        if return_url is not None:
            params["return_url"] = return_url
        resp = self._get("/users/me/subscription/portal", params=params)
        return resp.json()["portal_url"]
