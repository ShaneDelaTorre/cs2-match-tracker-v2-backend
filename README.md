# CS2 Match Tracker v2 — Backend
 
A Django/DRF REST API with WebSocket support, event sourcing, real-time chat, and a Celery-powered activity feed.
 
---
 
## Tech Stack
 
- **Python 3.13** + **Django 6.x** + **Django REST Framework**
- **PostgreSQL 16** — primary database
- **Redis 7** — channel layer (WebSockets) + task broker (Celery)
- **Django Channels + Uvicorn** — ASGI server for WebSocket support
- **Celery + Celery Beat** — background task queue and scheduler
- **SimpleJWT** — JWT authentication via httpOnly cookies
- **uv** — package manager
- **Docker + Colima** — containerized local development
- **GitHub Actions** — CI pipeline
- **pytest + factory-boy** — testing
- **ruff** — linting and formatting
---
 
## Architecture
 
### Layered separation of concerns
 
```
models.py       → data shape and database constraints only
services/       → all business logic (plain Python functions)
serializers.py  → input validation and output shape only
views.py        → HTTP concerns only (auth checks, call service, return response)
core/           → shared permissions, pagination, filters
```
 
No business logic lives in models or views. Services are the single source of truth for application logic.
 
### Event Sourcing (matches)
 
Matches are built from immutable `RoundEvent` records — never updated, never deleted. `MatchStat` is derived from `RoundEvent` aggregations at write time. The `get_match_state_at_round()` service can reconstruct the exact game state at any point in the match's history by aggregating only the events up to a given round number.
 
### Real-time Chat (Django Channels)
 
WebSocket connections are handled by `ChatConsumer` via Django Channels over ASGI. Authentication happens at the ASGI middleware layer (`JWTAuthMiddleware`) before the consumer runs — the JWT cookie is read from the WebSocket handshake headers and validated using SimpleJWT.
 
Chat rooms use a deterministic naming convention: `chat_{min_user_id}_{max_user_id}`. Both users always resolve to the same Redis group regardless of who initiates. Redis acts as the channel layer — a shared pub/sub bus that delivers messages across all connected consumers.
 
Flow:
```
Frontend WebSocket → JWTAuthMiddleware → ChatConsumer.connect()
                                           → friendship check
                                           → group_add to Redis
                                           → accept()
                                           → send history
 
User sends message → ChatConsumer.receive_json()
                       → save to PostgreSQL
                       → group_send to Redis
                       → Redis delivers to all connections in group
                       → ChatConsumer.chat_message() on each consumer
                       → send_json to each WebSocket
```
 
### Activity Feed (Celery)
 
`NewsSource` records store RSS feed URLs. Celery Beat publishes a `fetch_news` task to Redis every 10 minutes. The Celery worker picks it up and uses `feedparser` to parse each RSS feed, creating `NewsItem` records via `get_or_create` (idempotent — safe to run multiple times). The frontend polls `GET /api/news/` and renders the latest items.
 
```
Celery Beat → publishes task to Redis every 10 min
Redis       → holds task queue
Celery Worker → BRPOP blocking on Redis
              → feedparser.parse(feed_url)
              → NewsItem.objects.get_or_create(url=url)
```
 
### Authentication
 
Cookie-based JWT — the backend sets `access_token` and `refresh_token` as httpOnly cookies on login. JavaScript cannot read them, eliminating XSS token theft. A custom `CookieJWTAuthentication` class reads the token from the cookie instead of the Authorization header. For WebSockets, a separate `JWTAuthMiddleware` reads the cookie from the ASGI scope headers before the consumer runs.
 
---
 
## Apps
 
| App | Responsibility |
|-----|---------------|
| `accounts` | User model, friend requests, career summary |
| `matches` | Match, RoundEvent, MatchStat — event sourcing core |
| `chat` | ChatMessage model, WebSocket consumer, REST history endpoint |
| `news` | NewsSource, NewsItem, Celery fetch task |
| `authentication` | Cookie JWT auth, login/logout/refresh views |
| `core` | Shared permissions, pagination, filters |
 
---
 
## Key Business Rules
 
- `headshots` in a round must always be ≤ `kills` in that round
- `RoundEvent` rows are append-only — never updated, never deleted
- `MatchStat` is always derived from `RoundEvent` aggregations — never set directly by a user
- Two users must have an accepted `FriendRequest` before they can chat
- A user's match history is private — other users can only see career summary
---
 
## Running Locally
 
```bash
# Start all services
docker-compose up
 
# Run migrations
docker-compose exec api python manage.py migrate
 
# Seed database
docker-compose exec api python manage.py seed
docker-compose exec api python manage.py seed_news
 
# Run tests
docker-compose run --rm test pytest
 
# Trigger news fetch manually
docker-compose exec api python manage.py shell -c "from news.tasks import fetch_news; fetch_news()"
```
 
---
 
## CI
 
GitHub Actions runs on push/PR to `main` and `develop`. Pipeline: `uv sync --frozen` → `uv run pytest --cov`. Uses an ephemeral PostgreSQL service container with the same env var names as `settings.py`.