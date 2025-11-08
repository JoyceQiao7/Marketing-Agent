# 🎯 Quick Reference: What YOU Need to Change

This is a **quick reference** for busy developers. For detailed instructions, see `CUSTOMIZATION_GUIDE.md`.

---

## 🔴 MANDATORY Changes (System Won't Work Without These)

### 1. Environment Variables
**File:** `.env` (create from `.env.example`)

```bash
# MUST CONFIGURE:
SUPABASE_URL=_______________  # Your Supabase URL
SUPABASE_KEY=_______________  # Your Supabase key
REDDIT_CLIENT_ID=___________  # Reddit API client ID
REDDIT_CLIENT_SECRET=________  # Reddit API secret
REDDIT_USERNAME=_____________  # Bot account username
REDDIT_PASSWORD=_____________  # Bot account password
MULAN_AGENT_URL=_____________  # Your Mulan Agent API
MULAN_AGENT_API_KEY=_________  # Your API key
```

**Where to get these:**
- Supabase: https://supabase.com (create free project)
- Reddit: https://www.reddit.com/prefs/apps (create script app)
- Mulan Agent: Contact your Mulan Agent provider

---

### 2. Database Setup
**File:** `scripts/schema.sql`

**Action:**
1. Open Supabase SQL Editor
2. Copy/paste entire `schema.sql` file
3. Click "Run"

---

### 3. Mulan Agent API Integration
**File:** `backend/agent/mulan_client.py`

**Lines to modify:** 26-90

**Current (template):**
```python
payload = {
    "question": question_text,
    "title": question_title,
    "task": "analyze_capability"
}
```

**Action:** Replace with YOUR Mulan Agent API format

---

### 4. Question Keywords
**File:** `backend/crawler/reddit_crawler.py`

**Line:** 135

**Current:**
```python
relevant_keywords = [
    'ai', 'video', 'generate', 'create',
    # ... generic terms
]
```

**Action:** Replace with YOUR product-specific keywords
```python
relevant_keywords = [
    'your_product_name',
    'your_use_case',
    'your_industry_terms',
    # Be specific!
]
```

---

### 5. Subreddit Selection
**File:** `.env`

**Current:**
```bash
REDDIT_SUBREDDITS=artificialintelligence,machinelearning,...
```

**Action:** Replace with YOUR target subreddits
```bash
REDDIT_SUBREDDITS=your_niche_subreddit,another_relevant_sub
```

**How to find:** Search for communities where your target users ask questions

---

## 🟡 RECOMMENDED Changes (For Better Results)

### 6. Response Template
**File:** `backend/agent/response_generator.py`

**Line:** 60

**Action:** Customize to match your brand voice

---

### 7. Confidence Threshold
**File:** `.env`

```bash
MIN_CONFIDENCE_SCORE=0.7  # Adjust based on your needs
```

**Guidance:**
- 0.9 = Very selective (fewer, higher quality)
- 0.7 = Balanced (recommended)
- 0.5 = More responses (lower quality)

---

### 8. Auto-Posting
**File:** `.env`

```bash
AUTO_POST_ENABLED=false  # Keep FALSE until tested!
```

**⚠️ Only enable after:**
1. Testing manual crawls
2. Reviewing generated responses
3. Verifying response quality

---

## 🟢 OPTIONAL Changes (Nice to Have)

### 9. Quora Crawler
**File:** `backend/crawler/quora_crawler.py`

**Status:** Template only (Quora has no API)

**Options:**
- Implement web scraping (requires maintenance)
- Use third-party service
- Skip Quora, focus on Reddit

---

### 10. Error Monitoring
**File:** `.env`

```bash
SENTRY_DSN=your_sentry_dsn  # Optional but recommended
```

**Get free account:** https://sentry.io

---

## ✅ Quick Start Sequence

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit with your values
nano .env  # Or use your favorite editor

# 3. Set up database
# (Copy schema.sql into Supabase SQL Editor)

# 4. Start system
docker-compose up -d

# 5. Test crawl (with AUTO_POST_ENABLED=false)
make crawl-reddit

# 6. Review questions
make questions

# 7. When satisfied, enable auto-posting
# Edit .env: AUTO_POST_ENABLED=true
# Restart: docker-compose restart
```

---

## 📋 Pre-Launch Checklist

Before enabling auto-posting:

- [ ] Database tables created in Supabase
- [ ] All API credentials configured in `.env`
- [ ] Mulan Agent integration tested
- [ ] Keyword filters customized
- [ ] Test crawl completed successfully
- [ ] Generated responses reviewed
- [ ] Response quality meets standards
- [ ] Platform rules reviewed (Reddit/Quora ToS)
- [ ] Rate limits configured appropriately
- [ ] Monitoring set up (logs, Sentry)

---

## 🚨 Common Mistakes to Avoid

1. ❌ Enabling auto-posting without testing
2. ❌ Using generic keywords (won't find relevant questions)
3. ❌ Not customizing Mulan Agent integration (will fail)
4. ❌ Ignoring platform rules (will get banned)
5. ❌ Setting MIN_CONFIDENCE_SCORE too low (spam-like responses)
6. ❌ Not monitoring logs (won't see errors)

---

## 🎯 Files You MUST Edit Summary

| File | What to Change | Priority |
|------|---------------|----------|
| `.env` | All credentials & config | 🔴 CRITICAL |
| `scripts/schema.sql` | Run in Supabase | 🔴 CRITICAL |
| `backend/agent/mulan_client.py` | API integration | 🔴 CRITICAL |
| `backend/crawler/reddit_crawler.py` | Keywords (line 135) | 🔴 CRITICAL |
| `.env` | Subreddit list | 🔴 CRITICAL |
| `backend/agent/response_generator.py` | Response format | 🟡 Recommended |
| `.env` | Confidence threshold | 🟡 Recommended |
| `backend/crawler/quora_crawler.py` | Implement or skip | 🟢 Optional |

---

## 🆘 Need Help?

1. **Setup issues?** → Read `QUICK_START.md`
2. **Customization details?** → Read `CUSTOMIZATION_GUIDE.md`
3. **Architecture questions?** → Read `README.md`
4. **Implementation overview?** → Read `IMPLEMENTATION_SUMMARY.md`

---

## 💡 Pro Tips

1. **Start small:** Test with 1-2 subreddits first
2. **Monitor closely:** Check logs daily for first week
3. **Iterate keywords:** Refine based on results
4. **Be helpful:** Focus on value, not just promotion
5. **Stay compliant:** Read and follow platform rules

---

## ⏱️ Time Estimates

- ✅ Basic setup: 15 minutes
- ⚠️ Mulan Agent integration: 1-2 hours (depends on your API)
- ⚠️ Keyword customization: 30 minutes
- ⚠️ Testing and refinement: 2-4 hours
- 🎯 **Total to first auto-post:** 4-7 hours

---

**That's it! Focus on the 🔴 CRITICAL items first, then move to recommended changes.**

Good luck! 🚀

