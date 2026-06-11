"""Clubs API resource."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from ._resource import Resource
from .models import Club, EmailInvitation, PaginatedResult, ClubMember


class ClubsResource(Resource):
    """Endpoints under /clubs."""

    # ------------------------------------------------------------------
    # Club CRUD
    # ------------------------------------------------------------------

    def create(self, name: str, description: str | None = None) -> Club:
        """Create a new club."""
        body: dict = {"name": name}
        if description is not None:
            body["description"] = description
        resp = self._post("/clubs", json=body)
        return Club.model_validate(resp.json())

    def list(self) -> PaginatedResult[Club]:
        """List all clubs the current user belongs to."""
        resp = self._get("/clubs")
        data = resp.json()
        return PaginatedResult[Club](
            items=[Club.model_validate(c) for c in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def get(self, club_id: UUID | str) -> Club:
        """Get details of a specific club."""
        resp = self._get(f"/clubs/{club_id}")
        return Club.model_validate(resp.json())

    def update(
        self,
        club_id: UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Club:
        """Update club details (admin only)."""
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        resp = self._patch(f"/clubs/{club_id}", json=body)
        return Club.model_validate(resp.json())

    def delete(self, club_id: UUID | str) -> None:
        """Delete a club (admin only)."""
        resp = self._delete(f"/clubs/{club_id}")

    # ------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------

    def list_members(self, club_id: UUID | str) -> PaginatedResult[ClubMember]:
        """List members of a club."""
        resp = self._get(f"/clubs/{club_id}/members")
        data = resp.json()
        return PaginatedResult[ClubMember](
            items=[ClubMember.model_validate(u) for u in data.get("items", {}).items()],
            next_cursor=data.get("next_cursor"),
        )

    def remove_member(self, club_id: UUID | str, user_id: UUID | str) -> None:
        """Remove a member from a club (admin only)."""
        resp = self._delete(f"/clubs/{club_id}/members/{user_id}")

    def transfer_admin(self, club_id: UUID | str, new_admin_user_id: UUID | str) -> Club:
        """Transfer admin role to another member (admin only)."""
        resp = self._post(
            f"/clubs/{club_id}/admin",
            json={"new_admin_user_id": str(new_admin_user_id)},
        )
        return Club.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Invite code
    # ------------------------------------------------------------------

    def regenerate_invite_code(self, club_id: UUID | str) -> Club:
        """Regenerate the club's invite code (admin only)."""
        resp = self._post(f"/clubs/{club_id}/invite-code")
        return Club.model_validate(resp.json())

    def accept_email_invitation(self, club_id: UUID, code: str) -> Club:
        """Accept a club invitation using an email invitation code."""
        resp = self._post(f"/clubs/{club_id}/invitations/{code}/accept")
        return Club.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Cover image
    # ------------------------------------------------------------------

    def upload_cover_image(self, club_id: UUID | str, image_path: str | Path) -> Club:
        """Upload a cover image for a club (admin only)."""
        with open(image_path, "rb") as f:
            resp = self._post(f"/clubs/{club_id}/cover-image", files={"image": f})
        return Club.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Email invitations
    # ------------------------------------------------------------------

    def create_invitations(self, club_id: UUID | str, emails: list[str]) -> PaginatedResult[EmailInvitation]:
        """Send email invitations to a list of addresses (admin only)."""
        resp = self._post(f"/clubs/{club_id}/invitations", json={"emails": emails})
        data = resp.json()
        return PaginatedResult[EmailInvitation](
            items=[EmailInvitation.model_validate(i) for i in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def list_invitations(self, club_id: UUID | str) -> PaginatedResult[EmailInvitation]:
        """List pending email invitations for a club (admin only)."""
        resp = self._get(f"/clubs/{club_id}/invitations")
        data = resp.json()
        return PaginatedResult[EmailInvitation](
            items=[EmailInvitation.model_validate(i) for i in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )
