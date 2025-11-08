"""
Celery application configuration.
"""
from celery import Celery
from celery.schedules import crontab
from backend.config.settings import settings
from backend.utils.logger import log


# Initialize Celery
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

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "crawl-all-platforms": {
        "task": "backend.tasks.crawl_tasks.scheduled_crawl_all",
        "schedule": crontab(hour=f"*/{settings.crawl_interval_hours}"),
        "args": ()
    },
    "process-pending-questions": {
        "task": "backend.tasks.response_tasks.process_pending_questions_task",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
        "args": ()
    },
}

log.info("Celery application configured")

