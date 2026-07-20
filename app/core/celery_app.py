from celery import Celery
from app.config import settings

celery_app = Celery(
    "tiba_mkononi",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.generate_reports",
        "app.tasks.send_notifications",
        "app.tasks.process_emergency",
        "app.tasks.sync_inventory",
        "app.tasks.forecast_demand",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
