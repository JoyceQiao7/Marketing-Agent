"""
Tests for crawler implementations.
"""
import pytest
from datetime import datetime
from backend.crawler.reddit_crawler import RedditCrawler
from backend.crawler.quora_crawler import QuoraCrawler
from backend.database.models import QuestionCreate


@pytest.mark.asyncio
async def test_reddit_crawler_init():
    """Test Reddit crawler initialization."""
    crawler = RedditCrawler()
    assert crawler.platform_name == "reddit"
    assert crawler.reddit is not None


@pytest.mark.asyncio
async def test_quora_crawler_init():
    """Test Quora crawler initialization."""
    crawler = QuoraCrawler()
    assert crawler.platform_name == "quora"


# Add more tests as needed
# Note: These tests may require mocking external API calls

