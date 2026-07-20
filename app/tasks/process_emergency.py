from app.core.celery_app import celery_app

@celery_app.task
def process_emergency_dispatch(emergency_id: str):
    pass
