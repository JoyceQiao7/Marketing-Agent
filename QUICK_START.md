# 🚀 Quick Start Guide

Get the Mulan Marketing Agent up and running in 15 minutes!

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Supabase account
- Reddit account and API credentials

## Step 1: Clone and Setup

```bash
cd Mulan-Marketing-Agent
```

## Step 2: Create Environment File

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Required values:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key
- `REDDIT_CLIENT_ID` - From Reddit app settings
- `REDDIT_CLIENT_SECRET` - From Reddit app settings
- `REDDIT_USERNAME` - Your Reddit bot account
- `REDDIT_PASSWORD` - Your Reddit bot password
- `MULAN_AGENT_URL` - Your Mulan Agent API endpoint
- `MULAN_AGENT_API_KEY` - Your Mulan Agent API key

## Step 3: Set Up Database

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Run the SQL from `scripts/schema.sql`

Or:
```bash
python scripts/setup_db.py  # Shows the SQL to run
```

## Step 4: Start Services (Docker - Recommended)

```bash
docker-compose up -d
```

This starts:
- ✅ Redis (for Celery & rate limiting)
- ✅ FastAPI server (port 8000)
- ✅ Celery worker (background tasks)
- ✅ Celery beat (scheduler)
- ✅ Flower (Celery monitoring on port 5555)

## Step 5: Test the System

### Check if services are running:
```bash
# API health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# View Celery monitoring
open http://localhost:5555
```

### Trigger a manual crawl:
```bash
# Crawl Reddit
curl -X POST http://localhost:8000/api/crawl/reddit

# Check questions
curl http://localhost:8000/api/questions
```

## Step 6: Review and Customize

Before enabling auto-posting:

1. Check crawled questions: `http://localhost:8000/api/questions`
2. Review CUSTOMIZATION_GUIDE.md
3. Customize keyword filters
4. Test response generation
5. **Only then** set `AUTO_POST_ENABLED=true`

## Alternative: Local Development (Without Docker)

### 1. Install Python dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Redis:
```bash
redis-server
```

### 3. Start services in separate terminals:

**Terminal 1 - API Server:**
```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
cd backend
celery -A tasks.celery_app beat --loglevel=info
```

## Next Steps

1. ✅ Review [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for required changes
2. ✅ Customize question filtering keywords
3. ✅ Update Mulan Agent integration
4. ✅ Test manually before enabling auto-posting
5. ✅ Monitor logs and adjust settings

## Common Commands

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Seed test data
python scripts/seed_data.py

# Run tests
pytest tests/
```

## Troubleshooting

**Services won't start:**
- Check if ports 8000, 6379, 5555 are available
- Verify .env file exists and has all required variables

**No questions being crawled:**
- Check Reddit credentials
- Review keyword filters (may be too restrictive)
- Check logs: `docker-compose logs celery_worker`

**Mulan Agent errors:**
- Verify MULAN_AGENT_URL is correct
- Check API key is valid
- Review CUSTOMIZATION_GUIDE.md for API integration

## Support

For detailed customization instructions, see [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md).

For the full system architecture, see [README.md](README.md).

