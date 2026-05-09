"""Pydantic models for the Friday Movie Club API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
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
    completed = "completed"
    cancelled = "cancelled"
    archived = "archived"


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


class SubscriptionStatus(str, Enum):
    active = "active"
    past_due = "past_due"
    expired = "expired"
    cancelled = "cancelled"


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------


class User(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    role: UserRole
    email_verified: bool = False
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


class ClubMember(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
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
    start_time: datetime | None = None
    duration_minutes: int | None = None
    location: str | None = None
    status: EventStatus
    movie: Movie | None = None
    rsvps: list[EventRSVP] = Field(default_factory=list)
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


class AggregateRanking(BaseModel):
    movie_suggestion_id: UUID
    score: int
    movie: Movie | None = None


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


class SubscriptionPlan(BaseModel):
    id: UUID
    name: str
    price: Decimal
    currency_code: str
    interval_months: int
    max_clubs: int
    max_members: int
    active: bool
    created_at: datetime
    updated_at: datetime


class UserSubscription(BaseModel):
    id: UUID
    user_id: UUID
    status: SubscriptionStatus
    plan_id: UUID
    promo_code_id: UUID | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    max_clubs: int
    max_members: int
    updated_at: datetime


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
