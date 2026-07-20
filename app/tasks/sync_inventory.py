from app.core.celery_app import celery_app

@celery_app.task
def sync_inventory_from_csv(hospital_id: str, file_key: str):
    pass
