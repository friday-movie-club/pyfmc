"""Pydantic models for the Friday Movie Club API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class ClubStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class SuggestionStatus(str, Enum):
    active = "active"
    scheduled = "scheduled"
    watched = "watched"


class EventStatus(str, Enum):
    upcoming = "upcoming"
    past = "past"
    cancelled = "cancelled"


class RSVPStatus(str, Enum):
    going = "going"
    maybe = "maybe"
    not_going = "not_going"


class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"


class ScheduleStatus(str, Enum):
    active = "active"
    inactive = "inactive"


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------


class User(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserToken(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    last_used_at: datetime | None = None
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class Genre(BaseModel):
    id: int
    name: str


class Movie(BaseModel):
    id: UUID
    tmdb_id: int
    title: str
    overview: str
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    runtime: int | None = None
    genres: list[Genre] = Field(default_factory=list)
    vote_average: float | None = None
    cached_at: datetime


class MovieSuggestion(BaseModel):
    id: UUID
    club_id: UUID
    movie_id: UUID
    suggested_by: UUID
    status: SuggestionStatus
    movie: Movie | None = None


class Club(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    cover_image_url: str | None = None
    admin_user_id: UUID
    invite_code: str
    status: ClubStatus
    created_at: datetime
    updated_at: datetime


class Schedule(BaseModel):
    id: UUID
    club_id: UUID
    end_date: datetime | None = None
    day_of_week: int
    week_of_month: int
    status: ScheduleStatus
    created_at: datetime
    updated_at: datetime


class Event(BaseModel):
    id: UUID
    club_id: UUID
    movie_id: UUID | None = None
    schedule_id: UUID | None = None
    scheduled_at: datetime
    location: str | None = None
    status: EventStatus
    movie: Movie | None = None
    created_at: datetime
    updated_at: datetime


class EventRSVP(BaseModel):
    event_id: UUID
    user_id: UUID
    status: RSVPStatus
    updated_at: datetime


class EmailInvitation(BaseModel):
    id: UUID
    club_id: UUID
    email: str
    invited_by: UUID
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class AggregateRanking(BaseModel):
    suggestion_id: UUID
    score: int
    movie: Movie | None = None


# ---------------------------------------------------------------------------
# Paginated result
# ---------------------------------------------------------------------------

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None


# ---------------------------------------------------------------------------
# TMDB search
# ---------------------------------------------------------------------------


class TMDBSearchResult(BaseModel):
    id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    genre_ids: list[int] = Field(default_factory=list)


class TMDBSearchResponse(BaseModel):
    results: list[TMDBSearchResult]
    page: int
    total_results: int


# ---------------------------------------------------------------------------
# Auth response wrappers
# ---------------------------------------------------------------------------


class AuthResponse(BaseModel):
    user: User | None = None
    tokens: TokenPair
