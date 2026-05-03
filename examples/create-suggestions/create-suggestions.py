#!/usr/bin/env python

import json
import os
import sys

from fmc.client import FMCClient

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
    suggestions = []
    with open("suggestions.json") as file:
        suggestions = json.load(file)
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
    existing_suggestions: set[int] = set()
    for suggestion in client.movies.list(club_id, include_past=True).items:
        if suggestion.movie is not None:
            existing_suggestions.add(suggestion.movie.tmdb_id)

    for tmdb_id in suggestions:
        if tmdb_id not in existing_suggestions:
            print(f"Adding suggestion with TMDB ID {tmdb_id}")
            client.movies.suggest(club_id, tmdb_id)
