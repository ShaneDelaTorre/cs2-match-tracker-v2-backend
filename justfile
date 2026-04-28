# List all available commands
default:
    @just --list

# Build docker images
build:
    docker compose build

# Check running containers
ps:
    docker ps

# Check all containers
psa:
    docker ps -a

# Start all services
up:
    docker compose up

# Start all services in detached mode
upd:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Stop all services and remove volumes
down-v:
    docker compose down -v

# Run migrations
migrate:
    docker compose exec api python manage.py migrate

# Make migrations
makemigrations:
    docker compose exec api python manage.py makemigrations

# Create superuser
superuser:
    docker compose exec api python manage.py createsuperuser

# Django shell
shell:
    docker compose exec api python manage.py shell

# Open psql shell
psql:
    docker compose exec db psql -U cs2_tracker_user -d cs2_tracker

# Run tests
test:
    docker-compose run --rm test pytest

# Run tests with coverage
test-cov:
    docker-compose run --rm test pytest --cov

# Lint with ruff
lint:
    docker compose exec api ruff check .

# Format with ruff
format:
    docker compose exec api ruff format .

# View logs for all services
logs:
    docker compose logs -f

# View logs for a specific service (e.g. just logs-service api)
logs-service service:
    docker compose logs -f {{service}}

# Open a bash shell inside the api container
bash:
    docker compose exec api bash

# Run celery worker
worker:
    docker compose exec celery celery -A cs2_tracker worker -l info