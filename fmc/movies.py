"""Movies API resource."""

from __future__ import annotations

from uuid import UUID

from ._resource import Resource
from .models import AggregateRanking, MovieSuggestion, PaginatedResult, TMDBSearchResponse


class MoviesResource(Resource):
    """Movie suggestions and rankings within a club."""

    def suggest(self, club_id: UUID | str, tmdb_id: int) -> MovieSuggestion:
        """Suggest a movie for a club."""
        resp = self._post(f"/clubs/{club_id}/movies", json={"tmdb_id": tmdb_id})
        self._raise_for_status(resp)
        return MovieSuggestion.model_validate(resp.json())

    def list(self, club_id: UUID | str, include_past=None) -> PaginatedResult[MovieSuggestion]:
        """List all movie suggestions for a club."""
        url = f"/clubs/{club_id}/movies"
        if include_past is not None:
            if include_past is True:
                url += "?include_past=true"

        resp = self._get(url)
        self._raise_for_status(resp)
        data = resp.json()
        return PaginatedResult[MovieSuggestion](
            items=[MovieSuggestion.model_validate(s) for s in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def remove(self, club_id: UUID | str, movie_id: UUID | str) -> None:
        """Remove a movie suggestion (admin only)."""
        resp = self._delete(f"/clubs/{club_id}/movies/{movie_id}")
        self._raise_for_status(resp)

    def submit_ranking(self, club_id: UUID | str, ranked_movie_ids: list[UUID | str]) -> None:
        """Submit a ranked preference list of movie suggestion IDs."""
        resp = self._put(
            f"/clubs/{club_id}/rankings",
            json={"ranked_movie_ids": [str(mid) for mid in ranked_movie_ids]},
        )
        self._raise_for_status(resp)

    def aggregate_ranking(self, club_id: UUID | str) -> PaginatedResult[AggregateRanking]:
        """Get the aggregate Borda-count ranking for a club."""
        resp = self._get(f"/clubs/{club_id}/rankings/aggregate")
        self._raise_for_status(resp)
        data = resp.json()
        return PaginatedResult[AggregateRanking](
            items=[AggregateRanking.model_validate(r) for r in data.get("items", [])],
            next_cursor=data.get("next_cursor"),
        )

    def search_tmdb(self, query: str) -> TMDBSearchResponse:
        """Search The Movie Database for movies matching *query*."""
        resp = self._get("/tmdb/search", params={"q": query})
        self._raise_for_status(resp)
        return TMDBSearchResponse.model_validate(resp.json())
