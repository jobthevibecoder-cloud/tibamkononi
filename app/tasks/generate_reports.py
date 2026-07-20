from app.core.celery_app import celery_app

@celery_app.task
def generate_daily_report(hospital_id: str):
    pass

@celery_app.task
def generate_weekly_watchlist(county_id: str):
    pass
