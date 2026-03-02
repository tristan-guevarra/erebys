"""
celery application configuration for background jobs.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "erebys",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# schedule recurring tasks — metrics nightly, insights monday, pricing nightly
celery_app.conf.beat_schedule = {
    "aggregate-daily-metrics": {
        "task": "app.workers.tasks.aggregate_daily_metrics",
        "schedule": crontab(hour=1, minute=0),  # every day at 1:00 am utc
    },
    "generate-weekly-insights": {
        "task": "app.workers.tasks.generate_weekly_insights",
        "schedule": crontab(day_of_week=1, hour=6, minute=0),  # every monday 6:00 am utc
    },
    "refresh-pricing-recommendations": {
        "task": "app.workers.tasks.refresh_pricing_recommendations",
        "schedule": crontab(hour=3, minute=0),  # every day at 3:00 am utc
    },
}
