# 🔧 Customization Guide for Mulan Marketing Agent

This guide details **what YOU need to change** to make the system work for your specific use case. Follow this checklist carefully.

---

## 📋 Quick Start Checklist

- [ ] Set up Supabase database
- [ ] Configure environment variables
- [ ] Set up Reddit API credentials
- [ ] Configure Mulan Agent API integration
- [ ] Customize question filtering logic
- [ ] Customize response templates
- [ ] Test with manual crawl
- [ ] Enable auto-posting (when ready)

---

## 🔴 CRITICAL - Must Configure

### 1. Environment Variables (`.env` file)

**Location:** `/Mulan-Marketing-Agent/.env`

Create a `.env` file based on `.env.example` and configure:

```bash
# 1. SUPABASE CONFIGURATION (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_or_service_key

# 2. REDDIT API (REQUIRED)
# Get credentials from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=MulanMarketingAgent/1.0
REDDIT_USERNAME=your_reddit_bot_username
REDDIT_PASSWORD=your_reddit_bot_password

# 3. MULAN AGENT API (REQUIRED)
# Replace with your actual Mulan Agent API endpoint
MULAN_AGENT_URL=https://your-mulan-agent-api.com
MULAN_AGENT_API_KEY=your_mulan_agent_api_key
```

**📝 Action Required:**
- **Supabase:** Create a project at https://supabase.com
- **Reddit:** Create an app at https://www.reddit.com/prefs/apps (script type)
- **Mulan Agent:** Get your API endpoint and key from your Mulan Agent deployment

---

### 2. Database Setup

**Location:** `/scripts/schema.sql`

**Steps:**
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `scripts/schema.sql`
4. Click **Run** to create all tables and indexes

**Alternative:**
```bash
python scripts/setup_db.py  # This will show you the SQL to run
```

---

### 3. Mulan Agent Integration

**Location:** `/backend/agent/mulan_client.py`

**⚠️ IMPORTANT:** The Mulan Agent API integration is **currently a template**. You MUST modify these methods to match your actual Mulan Agent API:

#### Method 1: `analyze_question()` (Line 26)

**Current payload:**
```python
payload = {
    "question": question_text,
    "title": question_title,
    "task": "analyze_capability"
}
```

**What to change:**
- Update the `payload` structure to match your Mulan Agent's expected input format
- Modify the endpoint URL (`/api/analyze`) if different
- Update the response parsing logic based on your API's response format

**Expected response format:**
```python
{
    "is_in_scope": bool,        # Can Mulan handle this question?
    "confidence_score": float,  # 0.0 to 1.0
    "reasoning": str,           # Why is it in/out of scope
    "suggested_workflow": str   # Optional workflow link
}
```

#### Method 2: `generate_response()` (Line 62)

**What to change:**
- Update endpoint URL if different
- Modify payload structure to match your API
- Update response parsing

---

### 4. Question Filtering Logic

**Location:** `/backend/crawler/reddit_crawler.py` (Line 122-145)

**Method:** `_is_question()` and keyword filtering

**Current keywords:**
```python
relevant_keywords = [
    'ai', 'artificial intelligence', 'video', 'generate', 'create',
    'machine learning', 'deep learning', 'neural', 'animation',
    'editing', 'production', 'workflow'
]
```

**📝 Action Required:**
1. **Customize keywords** to match your product/service
2. **Add your specific terms:**
   - Your product name
   - Your industry-specific jargon
   - Competitor names (if you want to respond to those)
   - Use cases your product solves

**Example for a video editing SaaS:**
```python
relevant_keywords = [
    'your_product_name',
    'video editing',
    'video creation',
    'automatic subtitles',
    'video AI',
    # Add more relevant terms
]
```

**Location 2:** `/backend/crawler/quora_crawler.py` (Line 154)

Update the same keywords in `_is_relevant_question()`.

---

### 5. Response Templates

**Location:** `/backend/agent/response_generator.py` (Line 60-65)

**Current response format:**
```python
response_text += f"\n\nCheck out this workflow: {workflow_link}"
```

**📝 Action Required:**
Customize the response format to match your brand voice:

```python
# Example customization:
response_text = f"""
{response_data.get("response_text")}

---

💡 I created a workflow that can help with this: {workflow_link}

This workflow uses Mulan Agent to automate this process. Try it out!

*Disclaimer: I'm affiliated with Mulan Agent.*
"""
```

**Best Practices:**
- Be helpful first, promotional second
- Disclose affiliation with your product
- Add value to the conversation
- Follow platform rules (Reddit, Quora have strict self-promotion policies)

---

### 6. Subreddit and Topic Configuration

**Location:** `.env` file

**Current defaults:**
```bash
REDDIT_SUBREDDITS=artificialintelligence,machinelearning,deeplearning,videoproduction,videoediting
QUORA_TOPICS=Artificial Intelligence,Video Editing,Machine Learning
```

**📝 Action Required:**
1. Research relevant subreddits for your niche
2. Find Quora topics where your target audience hangs out
3. Start with 3-5 high-quality sources
4. Monitor which sources give best engagement

**Finding good subreddits:**
- Look for active communities (10k+ members)
- Check if self-promotion is allowed (read rules!)
- Look for weekly "promote your tool" threads
- Consider r/SaaS, r/startups, r/Entrepreneur

---

## 🟡 RECOMMENDED - Customize for Better Results

### 7. Rate Limiting

**Location:** `.env` file

```bash
MAX_REQUESTS_PER_MINUTE=30
CRAWL_INTERVAL_HOURS=6
```

**Recommendations:**
- **Reddit:** Stay under 60 requests/minute (API limit is 60)
- **Quora:** Be conservative (10-20 requests/minute) to avoid detection
- **Crawl Interval:** Start with 6-12 hours, adjust based on new content volume

---

### 8. Confidence Score Threshold

**Location:** `.env` file

```bash
MIN_CONFIDENCE_SCORE=0.7
```

**What this means:**
- Only questions with confidence ≥ 0.7 will get responses
- Lower = more responses (but less relevant)
- Higher = fewer responses (but more relevant)

**Recommended settings:**
- **Conservative (0.8-0.9):** High-quality leads, fewer false positives
- **Balanced (0.7):** Good mix of volume and quality
- **Aggressive (0.5-0.6):** More responses, but may miss the mark sometimes

---

### 9. Auto-Posting Control

**Location:** `.env` file

```bash
AUTO_POST_ENABLED=false  # Set to true when ready
```

**⚠️ CRITICAL:**
- Keep this as `false` during testing
- Manually review generated responses first
- Enable only after you're confident in:
  - Question filtering accuracy
  - Response quality
  - Compliance with platform rules

**Testing workflow:**
1. Run crawl: `curl -X POST http://localhost:8000/api/crawl/reddit`
2. Review questions: `curl http://localhost:8000/api/questions`
3. Generate responses (without posting): Set `AUTO_POST_ENABLED=false`
4. Review responses in database
5. Enable auto-posting only when satisfied

---

### 10. Quora Crawler Implementation

**Location:** `/backend/crawler/quora_crawler.py`

**⚠️ IMPORTANT:** The Quora crawler is a **template implementation** because:
1. Quora has no official API
2. Their HTML structure changes frequently
3. They have anti-bot measures

**What to do:**

#### Option A: Use Selenium (requires maintenance)
1. Inspect Quora's current HTML structure
2. Update selectors in `_extract_questions_from_page()` (Line 99)
3. Test frequently as Quora updates their site

#### Option B: Use a scraping service
1. Consider using a service like ScrapingBee or BrightData
2. Replace the crawler implementation with API calls

#### Option C: Focus on Reddit only
1. Comment out Quora in `crawler_manager.py`
2. Reddit API is stable and well-documented

**Current status:** Lines 99-150 are placeholder code. You must implement actual extraction logic.

---

### 11. Monitoring Configuration

**Location:** `.env` file

```bash
SENTRY_DSN=your_sentry_dsn  # Optional but recommended
LOG_LEVEL=INFO              # Set to DEBUG for development
```

**Recommended:**
- Set up Sentry (free tier available) for error tracking
- Use `LOG_LEVEL=DEBUG` during initial testing
- Switch to `LOG_LEVEL=INFO` in production

---

## 🟢 OPTIONAL - Advanced Customization

### 12. Add New Platforms

**Template:** Use `base_crawler.py` as reference

**Steps:**
1. Create new file: `backend/crawler/twitter_crawler.py`
2. Inherit from `BaseCrawler`
3. Implement:
   - `fetch_questions()`
   - `fetch_comments()`
   - `post_response()`
4. Register in `crawler_manager.py`

**Example platforms to add:**
- Twitter/X
- LinkedIn
- Stack Overflow
- Discord servers
- Slack communities

---

### 13. Custom Analytics

**Location:** `/backend/api/routes/analytics.py`

Add custom metrics:
- Response rate by platform
- Engagement metrics (upvotes, replies)
- Conversion tracking (if integrated with your product)
- Cost per response (API usage)

---

### 14. Webhook Integration

Add webhooks for:
- New question detected
- Response posted
- High-engagement opportunity
- Error alerts

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All environment variables set in `.env.production`
- [ ] Database migrations run successfully
- [ ] Manual testing completed (at least 10 questions)
- [ ] Response quality verified
- [ ] Platform rules reviewed (especially self-promotion policies)
- [ ] Rate limiting configured appropriately
- [ ] Error monitoring set up (Sentry)
- [ ] Auto-posting tested in development
- [ ] Backup plan for API failures
- [ ] Monitoring dashboard accessible

---

## 🧪 Testing Your Changes

### 1. Test Database Connection
```bash
python scripts/setup_db.py
```

### 2. Test Crawlers
```bash
# Start API
uvicorn backend.api.main:app --reload

# In another terminal:
curl -X POST http://localhost:8000/api/crawl/reddit
```

### 3. Test Mulan Agent Integration
```python
# Create test script: test_mulan.py
import asyncio
from backend.agent.mulan_client import mulan_client

async def test():
    result = await mulan_client.analyze_question(
        "How do I create AI videos?",
        "AI Video Creation Question"
    )
    print(result)

asyncio.run(test())
```

### 4. Test Response Generation
```bash
# Get a question ID from the database
curl http://localhost:8000/api/questions

# Generate response (with AUTO_POST_ENABLED=false)
curl -X POST http://localhost:8000/api/responses/{question_id}/generate
```

---

## 📞 Support & Next Steps

### If something doesn't work:

1. **Check logs:** `tail -f logs/mulan_agent_*.log`
2. **Verify environment variables:** `python -c "from backend.config.settings import settings; print(settings)"`
3. **Test API connections:** Use the health check endpoints
4. **Review error messages:** Most errors are configuration issues

### Common issues:

- **"Supabase connection failed"** → Check SUPABASE_URL and SUPABASE_KEY
- **"Reddit API error"** → Verify Reddit credentials and rate limits
- **"Mulan Agent timeout"** → Check MULAN_AGENT_URL and API availability
- **"No questions found"** → Adjust keyword filters or subreddit list

---

## 🎯 Summary: Minimum Required Changes

To get the system running, you MUST change:

1. ✅ `.env` file - All API credentials
2. ✅ Database setup - Run `schema.sql` in Supabase
3. ✅ `backend/agent/mulan_client.py` - Update API integration
4. ✅ `backend/crawler/reddit_crawler.py` - Customize keywords (Line 135)
5. ✅ `backend/agent/response_generator.py` - Customize response format (Line 60)
6. ✅ `.env` - Update `REDDIT_SUBREDDITS` to relevant communities

**Everything else can be customized gradually as you test and iterate.**

---

## 📚 Additional Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [Supabase Documentation](https://supabase.com/docs)
- [Celery Documentation](https://docs.celeryproject.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

Good luck! 🚀

