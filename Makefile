# Mulan Marketing Agent - Makefile
# Quick commands for development and deployment

.PHONY: help setup install clean test lint format run-api run-worker run-beat run-frontend docker-up docker-down

# Default target
help:
	@echo "🚀 Mulan Marketing Agent - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete setup (backend + frontend)"
	@echo "  make install        - Install all dependencies"
	@echo "  make clean          - Remove generated files and caches"
	@echo ""
	@echo "Development:"
	@echo "  make run-api        - Start FastAPI server"
	@echo "  make run-worker     - Start Celery worker"
	@echo "  make run-beat       - Start Celery beat scheduler"
	@echo "  make run-frontend   - Start Next.js dev server"
	@echo "  make run-all        - Start all services (requires tmux)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all services in Docker"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make docker-rebuild - Rebuild and restart Docker services"
	@echo ""
	@echo "CLI:"
	@echo "  make markets        - List all configured markets"
	@echo "  make crawl          - Trigger test crawl (specify MARKET=name)"
	@echo "  make leads          - Show leads (specify MARKET=name)"
	@echo ""

# Setup
setup:
	@echo "🔧 Running setup script..."
	@bash setup.sh

install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Installation complete!"

# Clean
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf backend/htmlcov
	rm -rf frontend/.next
	rm -rf frontend/out
	@echo "✅ Cleanup complete!"

# Development
run-api:
	@echo "🚀 Starting FastAPI server..."
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	@echo "⚙️  Starting Celery worker..."
	cd backend && celery -A tasks.celery_app worker --loglevel=info

run-beat:
	@echo "⏰ Starting Celery beat..."
	cd backend && celery -A tasks.celery_app beat --loglevel=info

run-frontend:
	@echo "🎨 Starting Next.js frontend..."
	cd frontend && npm run dev

run-all:
	@echo "🚀 Starting all services with tmux..."
	@command -v tmux >/dev/null 2>&1 || { echo "❌ tmux is required but not installed."; exit 1; }
	tmux new-session -d -s mulan 'cd backend && uvicorn api.main:app --reload' \; \
		split-window -v 'cd backend && celery -A tasks.celery_app worker -l info' \; \
		split-window -h 'cd backend && celery -A tasks.celery_app beat -l info' \; \
		select-pane -t 0 \; \
		split-window -h 'cd frontend && npm run dev' \; \
		attach-session -t mulan

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && pytest tests/ -v --cov=backend --cov-report=html
	@echo "✅ Tests complete! Coverage report: backend/htmlcov/index.html"

lint:
	@echo "🔍 Running linters..."
	cd backend && flake8 . --max-line-length=120 --exclude=venv,__pycache__
	cd backend && mypy . --ignore-missing-imports
	@echo "✅ Linting complete!"

format:
	@echo "✨ Formatting code..."
	cd backend && black . --exclude=venv
	cd backend && isort . --skip venv
	@echo "✅ Formatting complete!"

# Docker
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Docker services running!"
	@echo "   API: http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Flower: http://localhost:5555"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-rebuild:
	@echo "🔨 Rebuilding Docker services..."
	docker-compose down
	docker-compose up -d --build
	@echo "✅ Docker services rebuilt!"

# CLI Shortcuts
markets:
	@cd backend && python -m cli.main markets

crawl:
	@if [ -z "$(MARKET)" ]; then \
		echo "❌ Please specify MARKET=<name>"; \
		echo "   Example: make crawl MARKET=indie_authors"; \
		cd backend && python -m cli.main markets; \
	else \
		echo "🔍 Crawling market: $(MARKET)"; \
		cd backend && python -m cli.main crawl --market $(MARKET) --limit 10; \
	fi

leads:
	@if [ -z "$(MARKET)" ]; then \
		echo "❌ Please specify MARKET=<name>"; \
		echo "   Example: make leads MARKET=indie_authors"; \
	else \
		cd backend && python -m cli.main leads --market $(MARKET) --limit 10; \
	fi

stats:
	@if [ -z "$(MARKET)" ]; then \
		cd backend && python -m cli.main stats --days 7; \
	else \
		cd backend && python -m cli.main stats --market $(MARKET) --days 7; \
	fi

# Database
db-migrate:
	@echo "🗄️  Run this in your Supabase SQL editor:"
	@echo "   Copy and execute: scripts/schema.sql"

# Production
deploy:
	@echo "🚀 Deploying to production..."
	@echo "   1. Build backend: docker build -t mulan-backend ./backend"
	@echo "   2. Build frontend: cd frontend && npm run build"
	@echo "   3. Deploy to your cloud provider"
