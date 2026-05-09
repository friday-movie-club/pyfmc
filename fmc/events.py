"""Events API resource."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ._resource import Resource
from .models import Event, PaginatedResult, RSVPStatus


class EventScheduleInput:
    """Helper for specifying a recurring schedule when creating/updating an event."""

    def __init__(
        self,
        day_of_week: int,
        week_of_month: int,
        end_date: datetime | None = None,
    ) -> None:
        self.day_of_week = day_of_week
        self.week_of_month = week_of_month
        self.end_date = end_date

    def to_dict(self) -> dict:
        d: dict = {"day_of_week": self.day_of_week, "week_of_month": self.week_of_month}
        if self.end_date is not None:
            d["end"] = self.end_date.isoformat()
        return d


class EventsResource(Resource):
    """Event management within a club."""

    # ------------------------------------------------------------------
    # Listing / reading
    # ------------------------------------------------------------------

    def list(self, club_id: UUID | str, after: datetime | None = None) -> PaginatedResult[Event]:
        """List all events for a club."""
        url = f"/clubs/{club_id}/events"
        if after is not None:
            url += f"?after={after.strftime('%Y-%m-%d')}"
        resp = self._get(url)
        data = resp.json()
        return PaginatedResult[Event](
            items=[Event.model_validate(e) for e in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def get(self, club_id: UUID | str, event_id: UUID | str) -> Event:
        """Get details of a specific event."""
        resp = self._get(f"/clubs/{club_id}/events/{event_id}")
        return Event.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Admin CRUD
    # ------------------------------------------------------------------

    def create(
        self,
        club_id: UUID | str,
        start_time: datetime,
        end_time: datetime,
        *,
        timezone: str | None = None,
        location: str | None = None,
        movie_id: UUID | str | None = None,
        schedule: EventScheduleInput | None = None,
    ) -> Event:
        """Create an event (admin only)."""
        body: dict = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        if timezone is not None:
            body["timezone"] = timezone
        if location is not None:
            body["location"] = location
        if movie_id is not None:
            body["movie_id"] = str(movie_id)
        if schedule is not None:
            body["schedule"] = schedule.to_dict()
        resp = self._post(f"/clubs/{club_id}/events", json=body)
        return Event.model_validate(resp.json())

    def update(
        self,
        club_id: UUID | str,
        event_id: UUID | str,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        timezone: str | None = None,
        location: str | None = None,
        schedule: EventScheduleInput | None = None,
    ) -> Event:
        """Update an event (admin only)."""
        body: dict = {}
        if timezone is not None:
            body["timezone"] = timezone
        if start_time is not None:
            body["start_time"] = start_time.isoformat()
        if end_time is not None:
            body["end_time"] = end_time.isoformat()
        if location is not None:
            body["location"] = location
        if schedule is not None:
            body["schedule"] = schedule.to_dict()
        resp = self._patch(f"/clubs/{club_id}/events/{event_id}", json=body)
        return Event.model_validate(resp.json())

    def delete(self, club_id: UUID | str, event_id: UUID | str) -> None:
        """Delete an event (admin only)."""
        resp = self._delete(f"/clubs/{club_id}/events/{event_id}")

    # ------------------------------------------------------------------
    # Movie assignment
    # ------------------------------------------------------------------

    def assign_movie(self, club_id: UUID | str, event_id: UUID | str, movie_id: UUID | str) -> Event:
        """Assign a movie to an event (admin only)."""
        resp = self._put(
            f"/clubs/{club_id}/events/{event_id}/movie",
            json={"movie_id": str(movie_id)},
        )
        return Event.model_validate(resp.json())

    def remove_movie(self, club_id: UUID | str, event_id: UUID | str) -> Event:
        """Remove the assigned movie from an event (admin only)."""
        resp = self._delete(f"/clubs/{club_id}/events/{event_id}/movie")
        return Event.model_validate(resp.json())

    # ------------------------------------------------------------------
    # RSVP
    # ------------------------------------------------------------------

    def rsvp(self, club_id: UUID | str, event_id: UUID | str, status: RSVPStatus | str) -> None:
        """Submit or update an RSVP for an event."""
        self._put(
            f"/clubs/{club_id}/events/{event_id}/rsvp",
            json={"status": str(status.value if isinstance(status, RSVPStatus) else status)},
        )
