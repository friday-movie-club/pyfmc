# Friday Movie Club Client

Python client for the [Friday Movie Club](https://www.friday-movie.club) API.

`fmc` wraps the FMC REST API in a synchronous, typed client built on
[httpx](https://www.python-httpx.org/) and [pydantic](https://docs.pydantic.dev/).
Resources are exposed as attributes on a single `FMCClient`:

| Attribute | Purpose |
| --------- | ------- |
| `client.auth`   | Register, login (email/password or PAT), refresh tokens |
| `client.users`  | Current-user profile and personal access tokens |
| `client.clubs`  | Club CRUD, members, invitations, cover images |
| `client.movies` | Movie suggestions, rankings, TMDB search |
| `client.events` | Event CRUD, RSVPs, movie assignment |

## Requirements

- Python 3.12+

## Installation

```bash
pip install python-fmc
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add python-fmc
```

## Quickstart

```python
from fmc import FMCClient

with FMCClient(base_url="https://api.example.com/api/v1") as client:
    # Login with email/password (sets the access token on the client)
    client.auth.login(email="user@example.com", password="hunter2")

    # Or login with a Personal Access Token
    # client.auth.login(token="fmc_pat_...")

    # Create a club and list its members
    club = client.clubs.create("Friday Movie Club", description="Weekly hangout")
    members = client.clubs.list_members(club.id)

    for user in members.items:
        print(user.name, user.email)
```

If you already have an access token, pass it directly:

```python
client = FMCClient(base_url="...", token="eyJhbGciOi...")
```

## Errors

API errors are raised as subclasses of `FMCError`:

```python
from fmc import FMCClient, NotFoundError, ValidationError

try:
    club = client.clubs.get("00000000-0000-0000-0000-000000000000")
except NotFoundError:
    ...
except ValidationError as e:
    ...
```

Available exceptions: `APIError`, `AuthenticationError`, `ForbiddenError`,
`NotFoundError`, `ConflictError`, `ValidationError` — all inherit from `FMCError`.

## Examples

The [`examples/`](./examples) directory contains runnable scripts that
read `BASE_URL` and `AUTH_TOKEN` from the environment:

- `create-club/` — create a club if it doesn't already exist
- `create-suggestions/` — bulk-suggest movies from a JSON file
- `create-events/` — create movie-night events from a JSON file

```bash
export BASE_URL=https://api.example.com/api/v1
export AUTH_TOKEN=fmc_pat_...
python examples/create-club/create-club.py
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management
and [ruff](https://docs.astral.sh/ruff/) for linting.

```bash
uv sync
uv run ruff check
uv build
```
