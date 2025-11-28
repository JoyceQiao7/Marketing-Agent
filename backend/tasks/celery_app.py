"""
Celery application configuration with multi-market scheduling.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from celery import Celery
from celery.schedules import crontab
from backend.config.settings import settings
from backend.config.markets import get_all_markets, get_market_config
from backend.utils.logger import log

celery_app = Celery(
    "mulan_marketing_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "backend.tasks.crawl_tasks",
        "backend.tasks.response_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Configure periodic tasks with per-market schedules
beat_schedule = {}

# Add scheduled crawl for each market
markets = get_all_markets()
for market_name in markets:
    market_config = get_market_config(market_name)
    if market_config:
        # Schedule crawl based on market-specific interval
        beat_schedule[f"crawl-market-{market_name}"] = {
            "task": "backend.tasks.crawl_tasks.crawl_market_task",
            "schedule": crontab(hour=f"*/{market_config.crawl_interval_hours}"),
            "args": (market_name, 100)
        }

# Add general tasks
beat_schedule["process-pending-questions"] = {
    "task": "backend.tasks.response_tasks.process_pending_questions_task",
    "schedule": crontab(minute="*/30"),  # Every 30 minutes
    "args": ()
}

# Optional: Keep backwards-compatible general crawl
beat_schedule["crawl-all-platforms-fallback"] = {
    "task": "backend.tasks.crawl_tasks.scheduled_crawl_all_markets",
    "schedule": crontab(hour="*/12"),  # Every 12 hours as a fallback
    "args": ()
}

celery_app.conf.beat_schedule = beat_schedule

log.info(f"Celery application configured with {len(markets)} market schedules")
