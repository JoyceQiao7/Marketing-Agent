# Marketing-Agent

An automated system that crawls social media platforms (Quora, Reddit, etc.) for AI video-related questions, stores them in a database, processes them through an AI agent to determine if they're answerable, and automatically posts responses with workflow links.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start (15 Minutes)](#quick-start-15-minutes)
- [What You Need to Customize](#what-you-need-to-customize)
- [Database Schema](#database-schema)
- [System Workflow](#system-workflow)
- [API Endpoints](#api-endpoints)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Features

- 🤖 **Multi-platform Crawling**: Automated collection from Reddit, Quora, and extensible to other platforms
- 🧠 **AI Agent Integration**: Smart question filtering via Mulan Agent
- 💬 **Auto-Response**: Automatic reply posting with workflow links
- 🔄 **Deduplication**: Prevents processing duplicate questions
- ⚡ **Real-time Updates**: Live dashboard updates via Supabase
- 📊 **Analytics Dashboard**: Monitor crawling performance and agent responses
- 🛡️ **Rate Limiting**: Respects platform API limits
- 🔍 **Error Tracking**: Comprehensive logging and monitoring
x
---

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Task Queue**: Celery + Redis
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: PRAW (Reddit), Selenium (Quora)
- **Monitoring**: Loguru, Sentry

### Frontend (Optional)
- **Framework**: Next.js + TypeScript
- **UI Library**: Tailwind CSS
- **Features**: Monitoring, analytics, manual intervention

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Deployment**: Cloud Run / AWS ECS (backend), Vercel (frontend)

---

## Project Structure

```
Mulan-Marketing-Agent/
├── backend/
│   ├── crawler/
│   │   ├── base_crawler.py          # Abstract crawler class
│   │   ├── reddit_crawler.py        # Reddit implementation
│   │   ├── quora_crawler.py         # Quora implementation
│   │   └── crawler_manager.py       # Orchestrates crawlers
│   ├── agent/
│   │   ├── mulan_client.py          # Mulan Agent API client
│   │   ├── response_generator.py    # Response generation
│   │   └── capability_checker.py    # Question analysis
│   ├── database/
│   │   ├── models.py                # Pydantic models
│   │   ├── supabase_client.py       # Database operations
│   │   └── migrations/              # Migration scripts
│   ├── api/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── routes/                  # API endpoints
│   │   └── dependencies.py          # Shared dependencies
│   ├── tasks/
│   │   ├── celery_app.py           # Celery configuration
│   │   ├── crawl_tasks.py          # Crawling tasks
│   │   └── response_tasks.py       # Response tasks
│   ├── utils/
│   │   ├── logger.py               # Logging
│   │   ├── rate_limiter.py         # Rate limiting
│   │   └── deduplicator.py         # Duplicate detection
│   ├── config/
│   │   └── settings.py             # Configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                        # Optional dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── scripts/
│   ├── setup_db.py                 # Database initialization
│   ├── schema.sql                  # Supabase schema
│   └── seed_data.py                # Test data
├── tests/
│   ├── test_crawlers.py
│   ├── test_agent.py
│   └── test_api.py
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start (15 Minutes)

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Supabase account
- Reddit API credentials
- Mulan Agent API access

### 1. Clone and Setup

```bash
cd Mulan-Marketing-Agent
cp .env.example .env
# Edit .env with your credentials
```

### 2. Configure Environment Variables

**Required in `.env`:**
```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Reddit API (get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password

# Mulan Agent
MULAN_AGENT_URL=your_mulan_agent_api_url
MULAN_AGENT_API_KEY=your_api_key
```

### 3. Set Up Database

1. Go to Supabase SQL Editor
2. Copy and paste contents of `scripts/schema.sql`
3. Click "Run"

### 4. Start Services

**Using Docker (Recommended):**
```bash
docker-compose up -d
```

This starts:
- Redis (caching & task queue)
- FastAPI server (port 8000)
- Celery worker (background processing)
- Celery beat (scheduler)
- Flower (monitoring on port 5555)

**Without Docker:**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: API
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Celery Worker
cd backend
celery -A tasks.celery_app worker --loglevel=info

# Terminal 4: Celery Beat
cd backend
celery -A tasks.celery_app beat --loglevel=info
```

### 5. Test the System

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Trigger test crawl
curl -X POST http://localhost:8000/api/crawl/reddit

# Check questions
curl http://localhost:8000/api/questions
```

---

## What You Need to Customize

### 🔴 CRITICAL (Must Change)

#### 1. Mulan Agent API Integration
**File:** `backend/agent/mulan_client.py` (Lines 26-90)

Update the API payload and response parsing to match your Mulan Agent's actual API:

```python
# Current template - UPDATE THIS
payload = {
    "question": question_text,
    "title": question_title,
    "task": "analyze_capability"
}
```

#### 2. Question Keywords
**File:** `backend/crawler/reddit_crawler.py` (Line 135)

Customize keywords for your specific niche:

```python
relevant_keywords = [
    'your_product_name',
    'your_use_case',
    'your_industry_terms',
    # Add your specific keywords
]
```

#### 3. Subreddit Selection
**File:** `.env`

Choose relevant subreddits:

```bash
REDDIT_SUBREDDITS=your_niche_subreddit,another_relevant_sub
```

#### 4. Response Template
**File:** `backend/agent/response_generator.py` (Line 60)

Customize to match your brand voice:

```python
response_text = f"""
{response_data.get("response_text")}

Check out this workflow: {workflow_link}

*Disclosure: I'm affiliated with [Your Product]*
"""
```

### 🟡 RECOMMENDED

- **Confidence Threshold** (`.env`): Adjust `MIN_CONFIDENCE_SCORE=0.7`
- **Rate Limits** (`.env`): Fine-tune `MAX_REQUESTS_PER_MINUTE=30`
- **Auto-Posting**: Keep `AUTO_POST_ENABLED=false` until thoroughly tested

---

## Database Schema

### Tables

#### `questions`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| platform | ENUM | reddit, quora, etc. |
| post_id | STRING | Unique per platform |
| title | TEXT | Question title |
| content | TEXT | Question body |
| author | STRING | Username |
| url | STRING | Original post URL |
| tags | ARRAY | Related tags |
| upvotes | INTEGER | Score/upvotes |
| status | ENUM | pending, processing, answered, ignored |
| content_hash | STRING | For deduplication |
| created_at | TIMESTAMP | Original post date |
| crawled_at | TIMESTAMP | When crawled |

#### `comments`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| question_id | UUID | Foreign key → questions |
| comment_id | STRING | Unique per platform |
| content | TEXT | Comment text |
| author | STRING | Username |
| upvotes | INTEGER | Score/upvotes |
| created_at | TIMESTAMP | Comment date |

#### `agent_responses`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| question_id | UUID | Foreign key → questions |
| is_in_scope | BOOLEAN | Can agent answer? |
| confidence_score | FLOAT | Agent confidence |
| workflow_link | STRING | Link to workflow |
| response_text | TEXT | Generated response |
| posted | BOOLEAN | Posted successfully? |
| posted_at | TIMESTAMP | When posted |
| created_at | TIMESTAMP | Response generated |

#### `crawl_logs`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| platform | STRING | Platform name |
| status | ENUM | success, failure |
| items_found | INTEGER | Questions found |
| items_stored | INTEGER | Questions stored |
| error_message | TEXT | Error details |
| started_at | TIMESTAMP | Crawl start time |
| completed_at | TIMESTAMP | Crawl end time |

---

## System Workflow

```
┌─────────────────────┐
│  Scheduled Crawler  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Fetch Questions from│
│    Platforms        │
└──────────┬──────────┘
           │
           ▼
      ┌────────┐
      │Duplicate│  ──Yes──▶ Skip
      │ Check? │
      └────┬───┘
           │ No
           ▼
┌─────────────────────┐
│  Store in Supabase  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Queue for Processing│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Mulan Agent Analysis│
└──────────┬──────────┘
           │
           ▼
      ┌────────┐
      │In Scope?│
      └────┬───┘
       Yes │ No
           │  └──▶ Mark Ignored
           ▼
┌─────────────────────┐
│Generate Response +  │
│  Workflow Link      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Post to Platform    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Update Database     │
│   & Log Result      │
└─────────────────────┘
```

---

## API Endpoints

### Questions
- `GET /api/questions` - List questions (with filters)
- `GET /api/questions/{id}` - Get specific question
- `PATCH /api/questions/{id}` - Update question status
- `GET /api/questions/{id}/comments` - Get comments

### Responses
- `GET /api/responses/{question_id}` - Get agent response
- `POST /api/responses/{question_id}/generate` - Generate response
- `POST /api/responses/{question_id}/post` - Post response

### Crawling
- `POST /api/crawl/trigger` - Manual crawl (specific platform)
- `POST /api/crawl/trigger-all` - Crawl all platforms
- `POST /api/crawl/reddit` - Reddit-only crawl
- `POST /api/crawl/quora` - Quora-only crawl

### Analytics
- `GET /api/analytics` - Overall statistics
- `GET /api/analytics/crawl-logs` - Recent crawl logs

### Health
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger)

---

## Running the Application

### Development Mode

**With Docker:**
```bash
docker-compose up
```

**Without Docker:**
```bash
# Start from backend directory
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Useful Commands

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Seed test data
python scripts/seed_data.py

# Run tests
pytest tests/

# View Celery monitoring
open http://localhost:5555
```

---

## Testing

### Run Tests
```bash
cd backend
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=backend --cov-report=html
```

### Manual Testing
```bash
# Test crawl
curl -X POST http://localhost:8000/api/crawl/reddit

# Check results
curl http://localhost:8000/api/questions | jq

# View analytics
curl http://localhost:8000/api/analytics | jq
```

---

## Deployment

### Using Docker

**Backend (Cloud Run / AWS ECS):**
```bash
docker build -t your-registry/mulan-backend:latest ./backend
docker push your-registry/mulan-backend:latest

# Deploy to Cloud Run
gcloud run deploy mulan-backend \
  --image your-registry/mulan-backend:latest \
  --platform managed \
  --region us-central1
```

**Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

### Environment Variables for Production

Create `.env.production` with:
- Production database credentials
- Production API keys
- `ENVIRONMENT=production`
- `AUTO_POST_ENABLED=true` (after testing)
- Higher rate limits if needed

---

## Important Notes

### Before Enabling Auto-Posting

1. ✅ Test crawling manually
2. ✅ Review generated responses
3. ✅ Verify keyword filtering works
4. ✅ Check platform compliance
5. ✅ Set `AUTO_POST_ENABLED=false` initially
6. ✅ Monitor first 24 hours closely

### Platform Compliance

**Reddit:**
- Follow subreddit self-promotion rules
- Disclose affiliation
- Add value before promoting
- Respect rate limits

**Quora:**
- More strict on automation
- Manual posting may be safer
- Focus on providing value

### Security

- Use service role keys in production
- Enable Row Level Security in Supabase
- Never commit `.env` files
- Use secrets management in production
- Set up HTTPS/SSL

---

## Troubleshooting

**Import Errors:**
```bash
# Make sure you're running from correct directory
cd backend
uvicorn api.main:app --reload
```

**No Questions Found:**
- Check keyword filters (may be too restrictive)
- Verify Reddit credentials
- Check subreddit selection
- Review logs

**Mulan Agent Errors:**
- Verify API endpoint URL
- Check API key validity
- Update API integration code
- Test with curl first

**Database Connection Issues:**
- Verify Supabase URL and key
- Check network connectivity
- Review Row Level Security policies

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Support

For questions or issues, please open an issue on GitHub.

---

## Acknowledgments

- Mulan Agent team for AI processing
- Supabase for database infrastructure
- Reddit and Quora for platform APIs
