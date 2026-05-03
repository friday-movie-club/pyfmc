#!/usr/bin/env python

from datetime import datetime, timedelta
import json
import os
import sys
from zoneinfo import ZoneInfo

from fmc.client import FMCClient

from fmc.models import Event, Movie

club_name = "Friday Movie Club"
if __name__ == "__main__":
    env = {}
    base_url = os.getenv("BASE_URL", None)
    auth_token = os.getenv("AUTH_TOKEN", None)
    verify = False if os.getenv("VERIFY_TLS", "false").lower() == "false" else True

    if base_url is None or auth_token is None:
        print(
            "BASE_URL and AUTH_TOKEN environment variables are required.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = FMCClient(base_url=base_url, verify=verify)
    client.auth.login(token=auth_token)
    data = []
    with open("events.json") as file:
        data = json.load(file)
    club_id = None

    for club in client.clubs.list().items:
        if club.name == club_name:
            club_id = club.id
            break

    if club_id is None:
        print(
            f"Could not find movie club '{club_name}' you must create it first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load existing suggestions so that we can selectively
    # create them if they don't exist
    movies: dict[int, Movie] = {}
    for suggestion in client.movies.list(club_id, include_past=True).items:
        if suggestion.movie is not None:
            movies[suggestion.movie.tmdb_id] = suggestion.movie

    # Load existing events so we don't create duplicates
    events: dict[datetime, Event] = {}
    tzinfo = ZoneInfo("America/New_York")
    for event in client.events.list(club_id, after=datetime(2024, 1, 1)).items:
        if event.start_time is not None:
            event.start_time = event.start_time.astimezone(tzinfo)
            events[event.start_time] = event

    for event in data:
        if event["tmdb_id"] not in movies:
            print("Suggesting", event["movie"])
            suggestion = client.movies.suggest(club_id, event["tmdb_id"])
            if suggestion.movie is not None:
                movies[event["tmdb_id"]] = suggestion.movie

        # All of the events for this club start at 6:30 PM
        start_time = event["date"] + " 18:30"
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M").replace(
            tzinfo=tzinfo
        )
        if start_time not in events:
            client.events.create(
                club_id,
                start_time,
                start_time + timedelta(hours=4),
                location="Andrew's House",
                movie_id=movies[event["tmdb_id"]].id,
            )
        else:
            if events[start_time].movie is None:
                event_id = events[start_time].id
                client.events.assign_movie(
                    club_id, event_id, movies[event["tmdb_id"]].id
                )
