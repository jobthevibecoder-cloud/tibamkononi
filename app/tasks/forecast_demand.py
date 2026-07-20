from app.core.celery_app import celery_app

@celery_app.task
def forecast_demand(hospital_id: str):
    pass
