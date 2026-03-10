#!/usr/bin/env python

from datetime import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo

from fmc.client import FMCClient

from fmc.models import Event, Movie

if __name__ == "__main__":
    env = {}
    base_url=os.getenv("BASE_URL", None)
    auth_token=os.getenv("AUTH_TOKEN", None)
    verify=False if os.getenv("VERIFY_TLS", "false").lower() == "false" else True

    if base_url is None or auth_token is None:
        print("BASE_URL and AUTH_TOKEN environment variables are required.", file=sys.stderr)
        sys.exit(1)

    client = FMCClient(base_url=base_url, verify=verify)
    client.auth.login(token=auth_token)
    data = []
    with open("events.json") as file:
        data = json.load(file)
    club_id = ""

    # Find the uuid for the club named "Friday Movie Club"
    for club in client.clubs.list().items:
        if club.name == "Friday Movie Club":
            club_id = club.id
            break

    # Load existing suggestions so that we can selectively
    # create them if they don't exist
    movies: dict[int, Movie] = {}
    for suggestion in client.movies.list(club_id, include_past=True).items:
        if suggestion.movie is not None:
            movies[suggestion.movie.tmdb_id] = suggestion.movie

    # Load existing events so we don't create duplicates
    events: dict[datetime, Event] = {}
    tzinfo=ZoneInfo("America/New_York")
    for event in client.events.list(club_id, after=datetime(2024, 1, 1)).items:
        event.scheduled_at = event.scheduled_at.astimezone(tzinfo)
        events[event.scheduled_at] = event

    for event in data:
        if event["tmdb_id"] not in movies:
            print("Suggesting", event["movie"])
            suggestion = client.movies.suggest(club_id, event["tmdb_id"])
            if suggestion.movie is not None:
                movies[event["tmdb_id"]] = suggestion.movie

        # All of the events for this club start at 6:30 PM
        scheduled_at = event["date"] + " 18:30"
        scheduled_at = datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M").replace(tzinfo=tzinfo)
        if scheduled_at not in events:
            client.events.create(club_id, scheduled_at, location="Andrew's House", movie_id=movies[event["tmdb_id"]].id)
        else:
            if events[scheduled_at].movie is None:
                event_id = events[scheduled_at].id
                client.events.assign_movie(club_id, event_id, movies[event["tmdb_id"]].id)
