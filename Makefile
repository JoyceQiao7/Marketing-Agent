# Makefile for Mulan Marketing Agent

.PHONY: help install setup-db dev up down logs test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	cd backend && pip install -r requirements.txt

setup-db: ## Show database setup instructions
	@echo "Run this SQL in your Supabase SQL Editor:"
	@cat scripts/schema.sql

dev: ## Start development environment (Docker)
	docker-compose up

up: ## Start services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View API logs
	docker-compose logs -f api

logs-worker: ## View Celery worker logs
	docker-compose logs -f celery_worker

build: ## Rebuild Docker images
	docker-compose build

restart: ## Restart all services
	docker-compose restart

test: ## Run tests
	cd backend && pytest tests/ -v

test-cov: ## Run tests with coverage
	cd backend && pytest tests/ --cov=backend --cov-report=html

lint: ## Run linters
	cd backend && flake8 .
	cd backend && mypy .

format: ## Format code with black and isort
	cd backend && black .
	cd backend && isort .

clean: ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

seed: ## Seed database with test data
	python scripts/seed_data.py

crawl-reddit: ## Trigger manual Reddit crawl
	curl -X POST http://localhost:8000/api/crawl/reddit

crawl-all: ## Trigger manual crawl for all platforms
	curl -X POST http://localhost:8000/api/crawl/trigger-all

questions: ## List all questions
	curl http://localhost:8000/api/questions | jq

analytics: ## Show analytics
	curl http://localhost:8000/api/analytics | jq

health: ## Check API health
	curl http://localhost:8000/health

docs: ## Open API documentation
	open http://localhost:8000/docs

flower: ## Open Celery monitoring
	open http://localhost:5555

shell: ## Open Python shell with context
	cd backend && python -i -c "from backend.config.settings import settings; from backend.database.supabase_client import db_client; print('Context loaded: settings, db_client')"

