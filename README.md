# Mulan Marketing Agent

A multi-market "vibe marketing" lead finder that discovers and engages potential customers across platforms. Automatically finds people expressing interest or pain around video creation, scores leads with AI, generates context-aware replies, and provides tools for human review and approval before posting.

## Features

- 🎯 **Multi-Market Support** - Target different segments (indie authors, course creators, HR/L&D, nonprofits, B2B)
- 🤖 **AI-Powered Crawling** - Automatically finds relevant posts on Reddit, Quora, and more
- ✍️ **Smart Responses** - Generates market-specific reply drafts tailored to each audience
- 👤 **Human-in-the-Loop** - Review and approve all responses before posting
- 📊 **Lead Scoring** - AI analyzes relevance and provides confidence scores
- 🔄 **Scheduled Crawling** - Per-market automated discovery with configurable intervals
- 💻 **CLI & Web UI** - Command-line tools and React dashboard for management

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# Or use Makefile
make setup
```

### Manual Setup

#### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- Supabase account
- Reddit API credentials
- Mulan AI API key

#### 1. Setup Database

Run in Supabase SQL Editor:

```bash
# Copy and execute scripts/schema.sql in Supabase
```

### 2. Configure Environment

Create `.env` in project root:

```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key

# Reddit API
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=MulanAgent/1.0
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Mulan Agent
MULAN_AGENT_URL=https://api.mulan.ai
MULAN_AGENT_API_KEY=your_key

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Settings
AUTO_POST_ENABLED=false
MIN_CONFIDENCE_SCORE=0.7
```

### 3. Install Dependencies

```bash
# Using Makefile (recommended)
make install

# Or manually
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 4. Start Services

**Option A: Using Makefile (recommended)**
```bash
# In separate terminals
make run-api        # Terminal 1
make run-worker     # Terminal 2
make run-beat       # Terminal 3
make run-frontend   # Terminal 4

# Or start all at once with tmux
make run-all
```

**Option B: Using Docker**
```bash
make docker-up
# Services will be available at:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Flower: http://localhost:5555
```

**Option C: Manual**

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

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd backend
celery -A tasks.celery_app beat --loglevel=info
```

**Terminal 4 - Frontend (Optional):**
```bash
cd frontend
npm run dev
```

### 5. Test the System

```bash
# Using Makefile
make markets                              # List available markets
make crawl MARKET=indie_authors          # Test crawl
make leads MARKET=indie_authors          # View leads

# Or using CLI directly
python -m backend.cli.main markets
python -m backend.cli.main crawl --market indie_authors --limit 5
python -m backend.cli.main leads --market indie_authors --limit 10

# Or use the web UI at http://localhost:3000
```

## Usage

### CLI Commands

```bash
# Daily Workflow
python -m backend.cli.main markets                        # List all markets
python -m backend.cli.main leads --market <market>        # View leads
python -m backend.cli.main show <question_id>             # View details
python -m backend.cli.main post <question_id> --approve   # Post response

# Batch Operations
python -m backend.cli.main batch-post --market <market> --min-score 0.85

# Manual Crawling
python -m backend.cli.main crawl --market <market>

# Analytics
python -m backend.cli.main stats --market <market> --days 7
```

### API Endpoints

```bash
# Get questions by market
GET /api/questions?market=indie_authors&status=pending&min_score=0.7

# List all markets
GET /api/questions/markets/list

# Trigger market crawl
POST /api/crawl/market/indie_authors?limit=100

# Crawl all markets
POST /api/crawl/trigger-all-markets
```

### Web Dashboard

Navigate to `http://localhost:3000` to:
- Filter leads by market and status
- Review generated responses
- Approve and post replies
- View analytics per market

## Project Structure

```
├── backend/           # Python FastAPI backend
│   ├── agent/        # AI & response generation
│   ├── api/          # REST endpoints
│   ├── cli/          # Command-line interface
│   ├── config/       # Settings & market configurations
│   ├── crawler/      # Platform crawlers (Reddit, Quora)
│   ├── database/     # Models & database operations
│   ├── tasks/        # Celery background jobs
│   └── utils/        # Shared utilities
├── frontend/         # Next.js React dashboard
│   └── src/
│       ├── components/  # UI components (MarketFilter, QuestionCard)
│       ├── pages/       # Routes (dashboard, questions)
│       ├── hooks/       # React hooks (useQuestions, useAnalytics)
│       └── lib/         # API client & types
├── scripts/          # Database schema & setup
├── tests/            # Test suite
├── Makefile         # Quick commands
└── setup.sh         # Automated setup
```

## Markets Configuration

Markets are defined in `backend/config/markets.py`. Each market includes:

- **Platforms**: Which platforms to crawl (reddit, quora, etc.)
- **Keywords**: Search terms specific to that market
- **Subreddits/Topics**: Where to find leads
- **Tone**: Response style (professional, creative, etc.)
- **Confidence Threshold**: Minimum score to generate responses
- **Crawl Interval**: How often to search for new leads

**Pre-configured Markets:**
- `indie_authors` - Self-published authors, book marketing
- `course_creators` - Online educators, e-learning
- `hr_professionals` - Corporate training, L&D
- `nonprofits` - Fundraising, donor engagement
- `b2b_industrial` - Product demos, technical docs
- `general_video` - General video creation queries

### Adding New Markets

Edit `backend/config/markets.py`:

```python
"my_new_market": MarketConfig(
    name="my_new_market",
    description="Target audience description",
    platforms=["reddit", "quora"],
    reddit=PlatformConfig(
        subreddits=["subreddit1", "subreddit2"],
        keywords=["keyword1", "keyword2"],
        min_upvotes=3
    ),
    tone="professional, helpful",
    target_pain="specific problems they face",
    mulan_context="context for AI responses",
    workflow_examples={
        "workflow_name": "https://app.mulan.ai/workflow/link"
    },
    min_confidence_score=0.70,
    crawl_interval_hours=6
)
```

## How It Works

1. **Discover** - Celery Beat schedules crawls per market (e.g., indie_authors every 6h)
2. **Crawl** - Platform-specific crawlers search for relevant posts using market keywords
3. **Score** - Mulan AI analyzes each post for relevance and quality
4. **Generate** - Creates context-aware reply drafts with market-specific tone
5. **Review** - View leads in CLI or web dashboard, filtered by market
6. **Approve** - Edit if needed, then post via platform API

## Database Schema

Key tables:
- `questions` - Crawled posts with market field
- `agent_responses` - AI-generated replies with scores
- `crawl_logs` - Crawl history per market
- `comments` - Post comments for context

See `scripts/schema.sql` for complete schema.

## Development

### Useful Commands

```bash
make help          # Show all available commands
make test          # Run tests with coverage
make lint          # Run code linters
make format        # Format code (Black + isort)
make clean         # Remove caches and temp files
make docker-up     # Start with Docker
make docker-down   # Stop Docker services
```

### Running Tests

```bash
make test
# Or manually
cd backend && pytest tests/ -v --cov=backend
```

### Code Quality

```bash
make format        # Auto-format code
make lint          # Check code quality
```

### Docker Deployment

```bash
make docker-up              # Start services
make docker-down            # Stop services
make docker-rebuild         # Rebuild and restart
```

## Important Notes

### Before Auto-Posting

1. ✅ Test crawling manually
2. ✅ Review generated responses
3. ✅ Verify platform compliance
4. ✅ Keep `AUTO_POST_ENABLED=false` initially
5. ✅ Monitor first 24 hours closely

### Platform Compliance

**Reddit:**
- Follow subreddit self-promotion rules
- Disclose affiliation clearly
- Provide genuine value
- Respect rate limits

**Quora:**
- More strict on automation
- Manual posting recommended initially
- Focus on helpful answers

## Troubleshooting

**No questions found:**
- Check keywords in market config
- Verify Reddit credentials
- Review logs in `backend/logs/`

**Import errors:**
- Ensure running from correct directory
- Set PYTHONPATH if needed

**Celery not scheduling:**
- Verify Redis is running
- Check celery beat is running
- Review market configurations

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Celery, Redis
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **AI**: Mulan Agent API
- **Platforms**: PRAW (Reddit), Selenium (Quora)

## License

MIT License

## Support

For questions or issues, open an issue on GitHub.
