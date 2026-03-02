.PHONY: up down build migrate seed test-backend worker dev-frontend logs

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.seed

test-backend:
	docker compose exec backend pytest tests/ -v --tb=short

worker:
	docker compose exec worker celery -A app.workers.celery_app worker -l info

dev-frontend:
	cd frontend && npm run dev

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-worker:
	docker compose logs -f worker

shell-backend:
	docker compose exec backend bash

shell-db:
	docker compose exec postgres psql -U erebys -d erebys

reset-db:
	docker compose exec backend alembic downgrade base
	docker compose exec backend alembic upgrade head
	docker compose exec backend python -m app.seed
