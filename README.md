# Mulan-Marketing-Agent

A multi-market "vibe marketing" lead finder for Mulan AI that automatically discovers relevant posts across platforms where people express pain or interest around making videos. The system uses a general crawler that switches between market-specific sub-crawlers (indie authors, course creators, HR/L&D, nonprofits, industrial B2B), scores leads, generates context-aware replies, and provides a UI for review and approval before posting.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Quick Start (15 Minutes)](#quick-start-15-minutes)
- [What You Need to Customize](#what-you-need-to-customize)
- [Database Schema](#database-schema)
- [System Workflow](#system-workflow)
- [API Endpoints](#api-endpoints)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Deployment](#deployment)
- [To-Do & Roadmap](#to-do--roadmap)

---

## Quick Reference

**New to this project?** Start here:
1. 📖 Read [Overview](#overview) to understand what this system does
2. 🏗️ Review [Project Architecture](#project-architecture) to see how components fit together
3. 🌊 Study [Data Flow](#data-flow) to understand the end-to-end process
4. 🚀 Follow [Quick Start](#quick-start-15-minutes) to get running in 15 minutes
5. ⚙️ Check [What You Need to Customize](#what-you-need-to-customize) for market-specific setup

**Want to add a new market?** → See [Phase 3: New Market Segments](#phase-3-new-market-segments)  
**Want to add a new platform?** → See [Phase 4: New Platform Integrations](#phase-4-new-platform-integrations)  
**Debugging issues?** → See [Troubleshooting](#troubleshooting)

---

## Overview

**Mulan Marketing Agent** is an intelligent "vibe marketing" lead finder that discovers and engages potential customers across multiple platforms and market segments. Instead of generic outbound marketing, it finds people already expressing interest or pain points related to video creation.

### How It Works

1. **Discovers** - Crawls platforms (Reddit, Quora, etc.) using market-specific keywords
2. **Scores** - Evaluates each post's relevance and quality using Mulan AI
3. **Generates** - Creates context-aware, market-tailored reply drafts
4. **Reviews** - Presents top leads in a dashboard for human approval
5. **Engages** - Posts approved replies via platform APIs

### Why This Approach Works

Traditional marketing: "Here's our product, buy it!"  
Vibe marketing: "I see you're struggling with X. Here's how I solved it..."

By responding to existing conversations where people are already seeking solutions, you:
- Build trust through genuine help
- Avoid spam filters and community backlash
- Focus energy on high-intent leads
- Scale personal outreach efficiently

### Key Differentiators
- **Multi-Market Support**: Target different customer segments with tailored messaging
- **Market-Aware Responses**: Adjusts tone, examples, and positioning per market
- **Human-in-the-Loop**: Maintains brand quality by requiring approval
- **Extensible Architecture**: Add new markets or platforms in minutes, not days
- **Context-Rich**: Considers upvotes, comments, author history for better scoring

---

## Features

### Core Capabilities
- 🎯 **Multi-Market Support**: Target different customer segments (indie authors, course creators, HR/L&D, nonprofits, B2B) with tailored messaging
- 🤖 **Multi-Platform Crawling**: Automated lead discovery from Reddit, Quora, and extensible to Twitter, LinkedIn, etc.
- 🧠 **AI-Powered Scoring**: Intelligent post relevance analysis via Mulan Agent
- ✍️ **Context-Aware Responses**: Generates market-specific reply drafts with appropriate tone and messaging
- 👤 **Human-in-the-Loop**: Review, edit, and approve all responses before posting
- 📊 **Market Analytics**: Track performance metrics per market segment

### Technical Features
- 🔄 **Smart Deduplication**: Content hash-based duplicate detection across platforms
- ⚡ **Real-time Updates**: Live dashboard updates via Supabase real-time subscriptions
- 🛡️ **Rate Limiting**: Respects platform API limits and prevents spam detection
- 🔍 **Comprehensive Logging**: Track crawls, responses, and posting outcomes
- 🐳 **Containerized**: Docker Compose setup for easy deployment
- 🔐 **Secure**: Environment-based configuration, API key management
- 🧪 **Tested**: Unit tests for crawlers, agents, and API endpoints

### Workflow Features
- 🎨 **Filterable Dashboard**: Browse leads by market, score, platform, or date
- 📝 **Inline Editing**: Modify AI-generated responses before posting
- 🚀 **One-Click Posting**: Approve and post directly from UI
- 📦 **Bulk Operations**: Approve/skip/ignore multiple posts at once
- 💻 **CLI Alternative**: Command-line tools for power users
- 📈 **Performance Tracking**: Monitor conversion rates and engagement per market

---

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Task Queue**: Celery + Redis
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: PRAW (Reddit), Selenium (Quora)
- **Monitoring**: Loguru, Sentry

### Frontend
- **Framework**: Next.js + TypeScript
- **UI Library**: Tailwind CSS
- **Features**: Lead filtering by market, response review, one-click posting

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Deployment**: Cloud Run / AWS ECS (backend), Vercel (frontend)

---

## Project Architecture

The system follows a modular, event-driven architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  - Filter leads by market                                    │
│  - Review top-scoring posts                                  │
│  - Approve/edit replies                                      │
│  - One-click posting                                         │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  - Endpoint routing                                          │
│  - Authentication                                            │
│  - Request validation                                        │
└───┬─────────────────────────┬───────────────────────────────┘
    │                         │
    ▼                         ▼
┌───────────────┐      ┌──────────────────────┐
│  Crawler      │      │  Agent System        │
│  Manager      │      │  - Capability Check  │
│               │      │  - Response Gen      │
│  ├─Reddit     │      │  - Market Context    │
│  ├─Quora      │      └──────────────────────┘
│  └─[Future]   │
└───┬───────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      Task Queue (Celery)                     │
│  - Scheduled crawls                                          │
│  - Async response generation                                 │
│  - Batch processing                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (Supabase)                        │
│  - questions (with market field)                             │
│  - agent_responses                                           │
│  - crawl_logs                                                │
│  - comments                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**1. Crawler Manager** (`backend/crawler/`)
- Orchestrates market-specific crawlers
- Routes crawl requests to appropriate sub-crawlers
- Handles deduplication and rate limiting
- Stores raw leads in database

**2. Agent System** (`backend/agent/`)
- `mulan_client.py`: Communicates with Mulan AI API
- `capability_checker.py`: Scores posts for relevance and quality
- `response_generator.py`: Generates market-aware reply drafts

**3. Task Queue** (`backend/tasks/`)
- Schedules periodic crawls per market
- Processes leads asynchronously
- Handles retry logic for failed tasks

**4. API Layer** (`backend/api/`)
- Exposes REST endpoints for frontend
- Handles authentication and validation
- Manages post approval workflow

**5. Frontend** (`frontend/`)
- Market filter and lead browsing
- Response review interface
- Posting approval workflow

---

## Project Structure

```
Mulan-Marketing-Agent/
├── backend/                         # Python backend services
│   ├── crawler/                     # Platform crawlers (extensible)
│   │   ├── base_crawler.py          # Abstract base class for all crawlers
│   │   │                            # Defines interface: crawl(), filter(), store()
│   │   ├── reddit_crawler.py        # Reddit API integration via PRAW
│   │   │                            # Searches subreddits with market-specific keywords
│   │   ├── quora_crawler.py         # Quora web scraping (Selenium)
│   │   │                            # Handles dynamic content loading
│   │   └── crawler_manager.py       # Routes to appropriate crawler per market
│   │                                # Manages crawler lifecycle and coordination
│   ├── agent/                       # AI-powered lead qualification
│   │   ├── mulan_client.py          # Mulan Agent API client
│   │   │                            # Sends posts for AI analysis
│   │   ├── response_generator.py    # Generates market-aware replies
│   │   │                            # Uses market context + post content
│   │   └── capability_checker.py    # Scores posts for relevance
│   │                                # Returns confidence score (0-1)
│   ├── database/                    # Data persistence layer
│   │   ├── models.py                # Pydantic models (type-safe)
│   │   │                            # Question, Response, Market, etc.
│   │   ├── supabase_client.py       # Supabase operations wrapper
│   │   │                            # CRUD operations, queries
│   │   └── migrations/              # Database migration scripts
│   ├── api/                         # REST API layer
│   │   ├── main.py                  # FastAPI app initialization
│   │   │                            # CORS, middleware, error handlers
│   │   ├── routes/                  # Endpoint definitions
│   │   │   ├── questions.py         # GET/filter questions by market
│   │   │   ├── responses.py         # View/approve/post responses
│   │   │   ├── crawl.py             # Trigger manual crawls
│   │   │   └── analytics.py         # Dashboard statistics
│   │   └── dependencies.py          # Shared dependencies (DB, auth)
│   ├── tasks/                       # Background job processing
│   │   ├── celery_app.py           # Celery configuration
│   │   │                            # Redis broker, result backend
│   │   ├── crawl_tasks.py          # Scheduled crawl tasks per market
│   │   │                            # @celery.task decorators
│   │   └── response_tasks.py       # Async response generation
│   │                                # Batch processing for efficiency
│   ├── utils/                       # Shared utilities
│   │   ├── logger.py               # Structured logging (Loguru)
│   │   ├── rate_limiter.py         # API rate limiting per platform
│   │   └── deduplicator.py         # Content hash-based deduplication
│   ├── config/
│   │   └── settings.py             # Environment-based configuration
│   │                                # Loads from .env, validates types
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Backend container definition
│
├── frontend/                        # React/Next.js dashboard
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── QuestionCard.tsx     # Display individual post with score
│   │   │   ├── CrawlButton.tsx      # Manual crawl trigger
│   │   │   ├── StatCard.tsx         # Analytics display
│   │   │   └── Layout.tsx           # Page wrapper with nav
│   │   ├── pages/                   # Route definitions
│   │   │   ├── index.tsx            # Dashboard home (analytics)
│   │   │   ├── questions.tsx        # Lead browser with market filter
│   │   │   └── _app.tsx             # Global app wrapper
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useQuestions.ts      # Fetch/filter questions
│   │   │   └── useAnalytics.ts      # Fetch dashboard stats
│   │   ├── lib/                     # Frontend utilities
│   │   │   ├── api.ts               # API client functions
│   │   │   └── types.ts             # TypeScript type definitions
│   │   └── styles/
│   │       └── globals.css          # Tailwind + custom styles
│   ├── public/
│   │   └── favicon.ico
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── scripts/                         # Setup and maintenance scripts
│   ├── setup_db.py                 # Initialize Supabase tables
│   ├── schema.sql                  # Database schema definition
│   │                                # Tables: questions, responses, markets, etc.
│   └── seed_data.py                # Test data for development
│
├── tests/                           # Test suite
│   ├── test_crawlers.py            # Crawler unit tests
│   ├── test_agent.py               # Agent integration tests
│   └── test_api.py                 # API endpoint tests
│
├── logs/                            # Application logs (gitignored)
├── docker-compose.yml               # Development environment
├── docker-compose.prod.yml          # Production configuration
├── .env.example                     # Environment variable template
├── Makefile                         # Common commands
├── pytest.ini                       # Test configuration
└── README.md                        # This file
```

### Key Design Patterns

1. **Abstract Base Crawler**: All platform crawlers inherit from `BaseCrawler`, ensuring consistent interface
2. **Market-Aware**: Each component can access market context to tailor behavior
3. **Async Processing**: Heavy tasks (crawling, AI analysis) run asynchronously via Celery
4. **Type Safety**: Pydantic models enforce data validation throughout the stack
5. **Separation of Concerns**: Clear boundaries between crawling, analysis, storage, and presentation

---

## Data Flow

Understanding how data moves through the system is crucial for debugging and extending functionality.

### 1. Crawl → Store Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Scheduled Trigger (Celery Beat)                         │
│ • Runs every N hours (configurable per market)                  │
│ • Triggers: crawl_market.delay(market_name="indie_authors")     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Crawler Manager Routing                                 │
│ • CrawlerManager.get_crawler(market="indie_authors")            │
│ • Returns: RedditCrawler with author-specific keywords          │
│ • Keywords: ["self-publishing", "book trailer", "author video"] │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Platform API Call                                       │
│ • RedditCrawler.search_posts(subreddits=["selfpublish"])       │
│ • Uses PRAW to fetch posts from last 24 hours                  │
│ • Filters by keywords + upvote threshold                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Deduplication Check                                     │
│ • Generate content_hash = hash(title + content)                 │
│ • Query DB: SELECT * WHERE content_hash = ?                     │
│ • If exists: Skip. If new: Continue                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Store in Database                                       │
│ • INSERT INTO questions (                                       │
│     platform, post_id, title, content, author,                  │
│     url, upvotes, market, status='pending', ...                 │
│   )                                                              │
│ • Returns: question_id (UUID)                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Trigger Analysis                                        │
│ • analyze_question.delay(question_id)                           │
│ • Queued for async processing                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Analysis → Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Question                                          │
│ • Get question from DB by ID                                    │
│ • Load market config (keywords, tone, target audience)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: AI Capability Check                                     │
│ • POST to Mulan Agent API:                                      │
│   {                                                              │
│     "content": question.content,                                │
│     "market": question.market,                                  │
│     "task": "analyze_capability"                                │
│   }                                                              │
│ • Response: { is_answerable: bool, confidence: float }          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Score?  │
               Low  │         │  High
            ────────┤         ├────────
            │       └─────────┘       │
            ▼                         ▼
┌─────────────────────┐   ┌──────────────────────────────────────┐
│ Mark as 'ignored'   │   │ STEP 3: Generate Response            │
│ Update status       │   │ • POST to Mulan Agent:               │
│ Log reason          │   │   { "task": "generate_response",     │
└─────────────────────┘   │     "content": question,             │
                          │     "market_context": {...} }        │
                          │ • Response: {                        │
                          │     "text": "...",                   │
                          │     "workflow_link": "...",          │
                          │     "tone": "helpful"                │
                          │   }                                  │
                          └───────────────┬──────────────────────┘
                                          │
                                          ▼
                          ┌──────────────────────────────────────┐
                          │ STEP 4: Store Response               │
                          │ • INSERT INTO agent_responses (      │
                          │     question_id,                     │
                          │     is_in_scope=true,                │
                          │     confidence_score,                │
                          │     response_text,                   │
                          │     workflow_link,                   │
                          │     posted=false,                    │
                          │     ...                              │
                          │   )                                  │
                          └──────────────────────────────────────┘
```

### 3. Review → Post Flow (Human-in-the-Loop)

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: User Opens Dashboard                                  │
│ • Navigate to /questions                                        │
│ • Select market filter: "Indie Authors"                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ API Call: GET /api/questions?market=indie_authors&status=pending│
│ • Backend queries Supabase                                      │
│ • Joins with agent_responses table                             │
│ • Orders by confidence_score DESC, upvotes DESC                 │
│ • Returns top 50 results                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: Display Question Cards                                │
│ • Shows: title, snippet, score, platform badge                  │
│ • Click to expand → Shows full post + generated reply           │
│ • User can: Edit reply, Approve, Skip, Mark as spam             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (User clicks "Approve & Post")
┌─────────────────────────────────────────────────────────────────┐
│ API Call: POST /api/responses/{question_id}/post                │
│ • Validates: User is authenticated                              │
│ • Validates: Question hasn't been answered yet                  │
│ • Validates: Response text exists                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Platform API Posting                                            │
│ • If platform=reddit:                                           │
│   - PRAW: submission.reply(response_text)                       │
│ • If platform=quora:                                            │
│   - Selenium: Navigate, login, find answer box, type, submit    │
│ • Handle rate limits & errors                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │Success? │
                Yes │         │  No
            ────────┤         ├────────
            │       └─────────┘       │
            ▼                         ▼
┌─────────────────────┐   ┌──────────────────────────────────────┐
│ Update Database:    │   │ Update Database:                     │
│ • posted = true     │   │ • posted = false                     │
│ • posted_at = now() │   │ • error_message = ...                │
│ • status = 'answered'│  │ • status = 'pending'                 │
│                      │   │ • Log for retry                      │
│ Notify user: ✅     │   │ Notify user: ❌                      │
└─────────────────────┘   └──────────────────────────────────────┘
```

### 4. Market Configuration Flow

Markets are defined in configuration and control crawler behavior:

```python
# Example: backend/config/markets.py
MARKETS = {
    "indie_authors": {
        "platforms": ["reddit", "quora"],
        "reddit": {
            "subreddits": ["selfpublish", "writing", "authors"],
            "keywords": ["book trailer", "author website", "book marketing"],
        },
        "tone": "encouraging, creative",
        "target_pain": "marketing their books, creating content",
        "mulan_context": "video for book promotion, author branding"
    },
    "course_creators": {
        "platforms": ["reddit", "twitter"],
        "reddit": {
            "subreddits": ["teachonline", "elearning", "onlineeducation"],
            "keywords": ["course video", "lecture recording", "student engagement"],
        },
        "tone": "professional, educational",
        "target_pain": "creating engaging course content",
        "mulan_context": "educational video, course content"
    },
    # ... more markets
}
```

**How Markets Are Used:**
1. **Crawler**: Determines which platforms, subreddits, and keywords to use
2. **Agent**: Provides context for scoring and response generation
3. **Frontend**: Enables filtering and market-specific analytics

---

## User Workflow Example

Here's a typical daily workflow using the system:

### Morning: Review New Leads

**Step 1: Open Dashboard**
```
Navigate to: http://localhost:3000/questions
```

**Step 2: Filter by Market**
```
Select "Indie Authors" from market dropdown
Results: 15 pending leads from last 24 hours
```

**Step 3: Review Top Lead**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔵 Reddit • r/selfpublish • 18 upvotes • Score: 0.89       │
├─────────────────────────────────────────────────────────────┤
│ Title: "Need help creating a book trailer for my debut     │
│         fantasy novel"                                      │
├─────────────────────────────────────────────────────────────┤
│ Post: I've finished my first fantasy novel and my          │
│ publisher wants a book trailer for marketing. I have no    │
│ video editing experience and the quotes I got from pros    │
│ are $2k+. Any suggestions for DIY tools?                   │
├─────────────────────────────────────────────────────────────┤
│ AI Response:                                                │
│                                                             │
│ Congrats on your debut novel! 🎉 Book trailers can         │
│ definitely be expensive when done professionally, but      │
│ there are accessible options for DIY.                      │
│                                                             │
│ For fantasy novels, you'll want something that captures    │
│ the mood and genre feel. I've had success with Mulan AI    │
│ for creating book trailers - you can describe your story   │
│ and it generates video content that matches. Here's a      │
│ workflow specifically for book trailers:                   │
│ https://app.mulan.ai/workflow/book-trailer                 │
│                                                             │
│ The great thing about AI tools is you can iterate until    │
│ it feels right, without paying per revision.               │
│                                                             │
│ *Disclosure: I work with Mulan AI*                         │
├─────────────────────────────────────────────────────────────┤
│ [Edit Response] [✅ Approve & Post] [Skip] [❌ Ignore]     │
└─────────────────────────────────────────────────────────────┘
```

**Step 4: Approve**
- User clicks "Approve & Post"
- System posts reply to Reddit
- Question status → "answered"
- User gets success notification with link to posted comment

### Afternoon: Batch Process Lower Scores

**Step 5: Review Medium-Score Leads**
```
Filter: Score 0.70-0.79
Action: Bulk review 10 leads
Result: Approve 3, Skip 7
```

### Evening: Check Analytics

**Step 6: View Performance**
```
Navigate to: http://localhost:3000/

Dashboard shows:
- 45 leads discovered today
- 8 responses posted
- 3 markets active
- Top performing market: Course Creators (avg score 0.83)
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

#### 1. Market Definitions
**File:** `backend/config/markets.py` (Create this file)

Define your target markets with specific configurations:

```python
MARKETS = {
    "indie_authors": {
        "platforms": ["reddit", "quora"],
        "reddit": {
            "subreddits": ["selfpublish", "writing", "authors"],
            "keywords": [
                "book trailer", "author website", "book marketing",
                "book cover video", "author branding", "book promotion"
            ],
            "min_upvotes": 3
        },
        "quora": {
            "topics": ["Self-Publishing", "Book Marketing", "Writing"],
            "keywords": ["publish my book", "market my book"]
        },
        "tone": "encouraging, creative, supportive",
        "target_pain": "marketing their books, creating compelling content",
        "mulan_context": "video for book promotion, author branding, book trailers",
        "workflow_examples": {
            "book_trailer": "https://app.mulan.ai/workflow/book-trailer",
            "author_intro": "https://app.mulan.ai/workflow/author-intro"
        }
    },
    "course_creators": {
        "platforms": ["reddit", "twitter"],
        "reddit": {
            "subreddits": ["teachonline", "elearning", "onlineeducation"],
            "keywords": [
                "course video", "lecture recording", "student engagement",
                "online course", "teaching video", "educational content"
            ],
            "min_upvotes": 5
        },
        "tone": "professional, educational, helpful",
        "target_pain": "creating engaging course content, lecture recordings",
        "mulan_context": "educational video, course content, student engagement",
        "workflow_examples": {
            "lecture_video": "https://app.mulan.ai/workflow/lecture",
            "course_promo": "https://app.mulan.ai/workflow/course-promo"
        }
    },
    # Add more markets: hr_professionals, nonprofits, b2b_industrial, etc.
}
```

#### 2. Mulan Agent API Integration
**File:** `backend/agent/mulan_client.py`

Update to pass market context:

```python
async def analyze_question(
    self, 
    question_id: str, 
    question_text: str, 
    market: str
) -> dict:
    market_config = MARKETS.get(market, {})
    
    payload = {
        "content": question_text,
        "market": market,
        "context": market_config.get("mulan_context"),
        "tone": market_config.get("tone"),
        "task": "analyze_capability"
    }
    
    # Send to your Mulan Agent API
    response = await self.http_client.post(
        f"{self.base_url}/analyze",
        json=payload,
        headers={"Authorization": f"Bearer {self.api_key}"}
    )
    
    return response.json()
```

#### 3. Response Template per Market
**File:** `backend/agent/response_generator.py`

Customize response generation to use market-specific tone:

```python
async def generate_response(
    self, 
    question_id: str, 
    question_text: str,
    market: str
) -> str:
    market_config = MARKETS.get(market, {})
    
    # Get AI-generated response
    ai_response = await self.mulan_client.generate_response(
        question_text, 
        market_config
    )
    
    # Select appropriate workflow link for this market
    workflow_link = self._select_workflow(question_text, market_config)
    
    # Format with market-specific tone
    response_text = f"""{ai_response.get("response_text")}

You might find this helpful: {workflow_link}

*Disclosure: I work with Mulan AI, which offers tools for creating videos easily.*
"""
    
    return response_text
```

#### 4. Environment Variables
**File:** `.env`

Set up your credentials:

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password

# Mulan Agent
MULAN_AGENT_URL=https://api.mulan.ai
MULAN_AGENT_API_KEY=your_api_key

# Quora (optional)
QUORA_EMAIL=your_email
QUORA_PASSWORD=your_password

# System Settings
MIN_CONFIDENCE_SCORE=0.7
MAX_REQUESTS_PER_MINUTE=30
AUTO_POST_ENABLED=false  # Keep false until tested!
```

### 🟡 RECOMMENDED

#### 5. Adjust Scoring Thresholds per Market
Some markets may need different confidence thresholds:

```python
# In backend/config/markets.py
"indie_authors": {
    # ...
    "min_confidence_score": 0.65,  # Lower threshold, more volume
},
"b2b_industrial": {
    # ...
    "min_confidence_score": 0.80,  # Higher threshold, higher quality
}
```

#### 6. Customize Crawl Frequency
**File:** `backend/tasks/celery_app.py`

```python
# Different schedules per market
beat_schedule = {
    'crawl-indie-authors': {
        'task': 'tasks.crawl_tasks.crawl_market',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'args': ('indie_authors',)
    },
    'crawl-course-creators': {
        'task': 'tasks.crawl_tasks.crawl_market',
        'schedule': crontab(hour='*/12'),  # Every 12 hours
        'args': ('course_creators',)
    },
}
```

#### 7. Fine-tune Rate Limits
Respect platform APIs:

```bash
# .env
REDDIT_MAX_POSTS_PER_DAY=20
REDDIT_MIN_DELAY_BETWEEN_POSTS=300  # 5 minutes in seconds
QUORA_MAX_ANSWERS_PER_DAY=5  # Quora is stricter
```

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
| market | STRING | Market segment (indie_authors, etc.) |
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

### End-to-End Flow with Multi-Market Support

```
┌─────────────────────────────────────────────────────────────────┐
│  Scheduled Crawler (Per Market)                                 │
│  • Celery Beat triggers: crawl_market("indie_authors")          │
│  • Runs every N hours (configurable)                            │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Crawler Manager                                                 │
│  • Loads market config (keywords, subreddits, tone)             │
│  • Routes to platform crawler: RedditCrawler, QuoraCrawler      │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Fetch Posts from Platforms                                      │
│  • Reddit: Search subreddits with market keywords               │
│  • Quora: Scrape topic pages                                    │
│  • Filter by date range (last 24-48 hours)                      │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
      ┌────────────┐
      │ Duplicate  │  ──Yes──▶ Skip (already crawled)
      │   Check?   │
      │ (content   │
      │   hash)    │
      └────┬───────┘
           │ No
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Store in Supabase                                               │
│  • questions table: platform, post_id, content, market, ...     │
│  • status = 'pending'                                            │
│  • Returns: question_id                                          │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Queue for AI Analysis                                           │
│  • Celery task: analyze_question.delay(question_id)             │
│  • Async processing (doesn't block crawler)                     │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Mulan Agent Analysis                                            │
│  • Send question + market context to AI                         │
│  • Returns: is_in_scope (bool), confidence_score (0-1)          │
│  • status = 'processing'                                         │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
      ┌────────────┐
      │ In Scope?  │
      │ confidence │
      │  > 0.7?    │
      └────┬───────┘
           │
      ┌────┴─────┐
      │          │
     No          Yes
      │          │
      ▼          ▼
┌──────────┐   ┌─────────────────────────────────────────────────┐
│  Mark as │   │  Generate Market-Aware Response                 │
│ 'ignored'│   │  • Use market tone (creative, professional)     │
│  status  │   │  • Include relevant workflow link               │
└──────────┘   │  • Add disclosure                               │
               │  • Store in agent_responses table               │
               └──────────────┬──────────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────────────────────────┐
               │  Notify Frontend (Real-time)                     │
               │  • Supabase real-time updates                    │
               │  • New question appears in dashboard             │
               │  • status = 'pending' (awaiting approval)        │
               └──────────────┬───────────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────────────────────────┐
               │  Human Review (Frontend)                         │
               │  • User filters by market: "Indie Authors"       │
               │  • Reviews top-scored posts                      │
               │  • Reads generated response                      │
               │  • Can edit response inline                      │
               │  • Decision: Approve / Skip / Edit               │
               └──────────────┬───────────────────────────────────┘
                              │
                         [User Approves]
                              │
                              ▼
               ┌──────────────────────────────────────────────────┐
               │  Post to Platform (API Call)                     │
               │  • If Reddit: PRAW submission.reply()            │
               │  • If Quora: Selenium automation                 │
               │  • Respect rate limits                           │
               │  • Handle errors with retry logic                │
               └──────────────┬───────────────────────────────────┘
                              │
                         ┌────┴─────┐
                         │ Success? │
                         └────┬─────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                   Yes                  No
                    │                   │
                    ▼                   ▼
         ┌──────────────────┐   ┌──────────────────┐
         │ Update Database  │   │ Log Error        │
         │ • posted = true  │   │ • posted = false │
         │ • posted_at=now()│   │ • error_message  │
         │ • status='answrd'│   │ • Allow retry    │
         └──────────────────┘   └──────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
               ┌──────────────────────────────────────────────────┐
               │  Update Frontend                                 │
               │  • Show success/error notification               │
               │  • Update question card status                   │
               │  • Log to crawl_logs table                       │
               └──────────────────────────────────────────────────┘
```

### Key Decision Points

1. **Deduplication**: Prevents reprocessing same post across multiple crawls
2. **AI Scoring**: Filters out irrelevant posts early (saves processing time)
3. **Human Approval**: Final quality gate before posting (prevents spam/errors)
4. **Error Handling**: Failed posts remain in queue for retry

### Parallel Processing

Multiple flows run concurrently:
- **Crawl**: Separate tasks per market (indie_authors, course_creators, etc.)
- **Analysis**: Celery workers process multiple questions in parallel
- **Posting**: Sequential per account (respects rate limits)

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

## CLI Usage (Alternative to UI)

For users who prefer command-line workflows, we provide a CLI tool:

### Setup CLI
```bash
cd backend
pip install click tabulate  # If not in requirements.txt
```

### Available Commands

**1. View Leads by Market**
```bash
python -m cli.main leads --market indie_authors --status pending --limit 10
```

Output:
```
┌────────────┬──────────────────────────────┬─────────┬──────────┬───────┐
│ ID         │ Title                        │ Platform│ Score    │ Upvotes│
├────────────┼──────────────────────────────┼─────────┼──────────┼───────┤
│ abc123...  │ Need help with book trailer  │ reddit  │ 0.89     │ 15    │
│ def456...  │ Best way to market my novel? │ reddit  │ 0.82     │ 12    │
└────────────┴──────────────────────────────┴─────────┴──────────┴───────┘
```

**2. View Generated Response**
```bash
python -m cli.main show-response abc123
```

**3. Approve and Post**
```bash
python -m cli.main post abc123 --approve
```

**4. Batch Approve Top Leads**
```bash
python -m cli.main batch-post --market indie_authors --min-score 0.85 --limit 5
```

**5. Trigger Manual Crawl**
```bash
python -m cli.main crawl --market course_creators
```

**6. Analytics**
```bash
python -m cli.main stats --market indie_authors --days 7
```

### CLI Implementation

Create `backend/cli/main.py`:

```python
import click
from tabulate import tabulate
from database.supabase_client import SupabaseClient
from agent.response_generator import ResponseGenerator

@click.group()
def cli():
    """Mulan Marketing Agent CLI"""
    pass

@cli.command()
@click.option('--market', required=True, help='Market segment')
@click.option('--status', default='pending', help='Question status')
@click.option('--limit', default=10, help='Number of results')
def leads(market, status, limit):
    """List top leads for a market"""
    db = SupabaseClient()
    questions = db.get_questions(
        market=market, 
        status=status, 
        limit=limit,
        order_by='confidence_score DESC'
    )
    
    table_data = [
        [
            q['id'][:8] + '...',
            q['title'][:30] + '...',
            q['platform'],
            f"{q['confidence_score']:.2f}",
            q['upvotes']
        ]
        for q in questions
    ]
    
    click.echo(tabulate(
        table_data,
        headers=['ID', 'Title', 'Platform', 'Score', 'Upvotes'],
        tablefmt='grid'
    ))

@cli.command()
@click.argument('question_id')
def show_response(question_id):
    """Show generated response for a question"""
    db = SupabaseClient()
    question = db.get_question(question_id)
    response = db.get_response(question_id)
    
    click.echo(f"\n{'='*60}")
    click.echo(f"QUESTION ({question['platform']})")
    click.echo(f"{'='*60}")
    click.echo(f"Title: {question['title']}")
    click.echo(f"URL: {question['url']}")
    click.echo(f"Content:\n{question['content']}\n")
    click.echo(f"{'='*60}")
    click.echo(f"GENERATED RESPONSE (Score: {response['confidence_score']})")
    click.echo(f"{'='*60}")
    click.echo(response['response_text'])
    click.echo(f"\n{'='*60}\n")

@cli.command()
@click.argument('question_id')
@click.option('--approve', is_flag=True, help='Approve and post')
def post(question_id, approve):
    """Post a response to the platform"""
    if not approve:
        click.echo("Use --approve flag to confirm posting")
        return
    
    # Import poster logic
    from api.routes.responses import post_response
    
    try:
        result = post_response(question_id)
        click.echo(f"✅ Posted successfully! {result['url']}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    cli()
```

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

## To-Do & Roadmap

### Current Status ✅
- [x] Core crawler architecture (Reddit, Quora)
- [x] Mulan Agent integration for AI analysis
- [x] Supabase database with proper schema
- [x] FastAPI backend with REST endpoints
- [x] Next.js frontend dashboard
- [x] Celery task queue for async processing
- [x] Basic deduplication system
- [x] Rate limiting per platform
- [x] Docker containerization

### Phase 1: Multi-Market Foundation (In Progress)
- [ ] **Market Configuration System**
  - [ ] Create `backend/config/markets.py` with market definitions
  - [ ] Add market-specific keyword sets
  - [ ] Define tone and context per market
  - [ ] Implement market selection in crawler manager

- [ ] **Update Database Schema**
  - [ ] Add `market` column to questions table (STRING)
  - [ ] Create `markets` lookup table (optional, for metadata)
  - [ ] Add indexes on `market` field for filtering
  - [ ] Migration script for existing data

- [ ] **Market-Aware Crawling**
  - [ ] Modify `CrawlerManager` to accept `market` parameter
  - [ ] Route to appropriate crawler with market config
  - [ ] Pass market keywords to platform APIs
  - [ ] Store market field with each question

- [ ] **Market-Aware Response Generation**
  - [ ] Pass market context to Mulan Agent API
  - [ ] Implement market-specific response templates
  - [ ] Adjust tone based on market configuration
  - [ ] Test responses for each market segment

### Phase 2: Enhanced UI/UX
- [ ] **Frontend Market Filtering**
  - [ ] Add market dropdown/tabs to questions page
  - [ ] Filter API calls by selected market
  - [ ] Show market badge on question cards
  - [ ] Market-specific analytics dashboard

- [ ] **Response Review Interface**
  - [ ] Expand question card to show full post
  - [ ] Display generated response in editable textarea
  - [ ] Add "Edit", "Approve", "Skip" buttons
  - [ ] Implement inline response editing
  - [ ] Show confidence score and reasoning

- [ ] **One-Click Posting**
  - [ ] Implement POST /api/responses/{id}/post endpoint
  - [ ] Handle platform-specific posting logic
  - [ ] Show real-time posting status
  - [ ] Error handling with retry option
  - [ ] Success notification with link to posted reply

- [ ] **Bulk Operations**
  - [ ] Select multiple questions (checkboxes)
  - [ ] Bulk approve/skip/ignore
  - [ ] Bulk export to CSV
  - [ ] Keyboard shortcuts for efficiency

### Phase 3: New Market Segments
Add these target markets (in priority order):

- [ ] **Indie Authors**
  - [ ] Define keywords: book trailer, author branding, book marketing
  - [ ] Platforms: Reddit (r/selfpublish, r/writing), Quora
  - [ ] Response template emphasizing creative storytelling

- [ ] **Course Creators / Online Educators**
  - [ ] Keywords: course video, lecture recording, student engagement
  - [ ] Platforms: Reddit (r/teachonline, r/elearning), Twitter
  - [ ] Response template emphasizing educational value

- [ ] **HR & L&D Professionals**
  - [ ] Keywords: training video, employee onboarding, corporate learning
  - [ ] Platforms: LinkedIn, Reddit (r/humanresources)
  - [ ] Professional tone, ROI-focused

- [ ] **Nonprofits**
  - [ ] Keywords: fundraising video, donor outreach, impact storytelling
  - [ ] Platforms: Reddit (r/nonprofit), Facebook Groups
  - [ ] Empathetic tone, mission-focused

- [ ] **Industrial B2B**
  - [ ] Keywords: product demo, technical documentation, sales enablement
  - [ ] Platforms: LinkedIn, Industry forums
  - [ ] Technical tone, efficiency-focused

### Phase 4: New Platform Integrations
- [ ] **Twitter/X Integration**
  - [ ] Implement `TwitterCrawler` class
  - [ ] Use Twitter API v2 for search
  - [ ] Handle tweet threads
  - [ ] Reply via Twitter API

- [ ] **LinkedIn Integration**
  - [ ] Implement `LinkedInCrawler` class
  - [ ] Search posts/articles via LinkedIn API
  - [ ] Handle authentication (OAuth)
  - [ ] Comment via API

- [ ] **Facebook Groups** (if feasible)
  - [ ] Research API limitations for groups
  - [ ] Implement crawler if API allows
  - [ ] Consider manual posting workflow

- [ ] **Discord Communities**
  - [ ] Bot integration for servers
  - [ ] Monitor specific channels
  - [ ] Direct message or thread replies

- [ ] **Slack Communities**
  - [ ] Similar to Discord integration
  - [ ] Monitor public Slack communities

### Phase 5: Advanced Features
- [ ] **Smart Scheduling**
  - [ ] Analyze best posting times per platform
  - [ ] Queue approved posts for optimal timing
  - [ ] Avoid posting too frequently to same subreddit

- [ ] **A/B Testing**
  - [ ] Generate multiple response variants
  - [ ] Track which responses get upvotes/engagement
  - [ ] Learn from high-performing responses

- [ ] **Sentiment Analysis**
  - [ ] Detect urgency/frustration in posts
  - [ ] Prioritize high-urgency leads
  - [ ] Adjust response tone based on sentiment

- [ ] **Lead Scoring 2.0**
  - [ ] Machine learning model for scoring
  - [ ] Factor in: author history, engagement, recency
  - [ ] Predict conversion likelihood

- [ ] **Analytics & Reporting**
  - [ ] Weekly summary emails
  - [ ] Conversion tracking (post → website visit)
  - [ ] ROI dashboard per market
  - [ ] A/B test results visualization

### Phase 6: Automation & Scaling
- [ ] **Semi-Automated Posting**
  - [ ] Auto-approve posts above confidence threshold
  - [ ] Daily digest of auto-posted replies
  - [ ] Emergency stop mechanism

- [ ] **Multi-Account Support**
  - [ ] Manage multiple Reddit/platform accounts
  - [ ] Rotate accounts to avoid spam detection
  - [ ] Track reputation per account

- [ ] **Webhook Integrations**
  - [ ] Slack notifications for new high-score leads
  - [ ] Discord bot for team review
  - [ ] Zapier/Make integration for workflows

- [ ] **API for External Tools**
  - [ ] Public API documentation
  - [ ] API keys for third-party access
  - [ ] Rate limiting for API consumers

### Phase 7: Compliance & Safety
- [ ] **Spam Prevention**
  - [ ] Max posts per subreddit per day
  - [ ] Cooldown period between posts
  - [ ] Blacklist for over-posted subreddits

- [ ] **Content Moderation**
  - [ ] Profanity filter for generated responses
  - [ ] Human review required for sensitive topics
  - [ ] Compliance checks per platform TOS

- [ ] **Privacy & Data Retention**
  - [ ] Auto-delete old posts (GDPR compliance)
  - [ ] Anonymize author data
  - [ ] User data export feature

### Phase 8: Enterprise Features (Future)
- [ ] **Multi-Tenant Support**
  - [ ] Multiple teams/companies on same instance
  - [ ] Separate databases per tenant
  - [ ] Billing integration

- [ ] **White-Label Solution**
  - [ ] Customizable branding
  - [ ] Custom domain support
  - [ ] Embeddable widgets

- [ ] **Advanced Integrations**
  - [ ] CRM integration (Salesforce, HubSpot)
  - [ ] Marketing automation (Mailchimp, ActiveCampaign)
  - [ ] Analytics platforms (Google Analytics, Mixpanel)

---

## Implementation Priority

**Focus Areas (Next 2-4 Weeks):**
1. ✅ Complete multi-market configuration system
2. ✅ Update database schema with market field
3. ✅ Implement market filtering in frontend
4. ✅ Add first 3 market segments (authors, educators, HR)
5. ✅ Build response review & approval UI
6. ✅ Implement one-click posting

**After MVP:**
- Add Twitter & LinkedIn platforms
- Implement smart scheduling
- Build analytics dashboard
- Add A/B testing for responses

---

## Support

For questions or issues, please open an issue on GitHub.

---

## Acknowledgments

- Mulan Agent team for AI processing
- Supabase for database infrastructure
- Reddit and Quora for platform APIs
