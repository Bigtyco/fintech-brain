.PHONY: up down build logs backend frontend db-migrate db-upgrade

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

db-migrate:
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd backend && alembic upgrade head

install-backend:
	cd backend && pip install -e .

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend
