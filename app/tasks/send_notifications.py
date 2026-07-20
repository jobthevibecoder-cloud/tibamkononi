from app.core.celery_app import celery_app

@celery_app.task
def send_sms(phone: str, message: str):
    pass

@celery_app.task
def send_push_notification(user_id: str, title: str, body: str):
    pass
