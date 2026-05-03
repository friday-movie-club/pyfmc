#!/usr/bin/env python

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

    club_id = None
    for club in client.clubs.list().items:
        if club.name == club_name:
            club_id = club.id
            break

    if club_id is None:
        print(f"Could not find club, creating {club_name}")
        client.clubs.create(club_name, "")
