from celery import Celery

from app.config import settings

celery = Celery(
    "gestronomy",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    timezone="UTC",
    result_serializer="json",
    accept_content=["json"],
    task_serializer="json",
)

celery.autodiscover_tasks([
    "app.accounting",
    "app.auth",
    "app.core",
    "app.dashboard",
    "app.digital_twin",
    "app.food_safety",
    "app.forecasting",
    "app.franchise",
    "app.guests",
    "app.inventory",
    "app.integrations",
    "app.maintenance",
    "app.marketing",
    "app.vision",
    "app.websockets",
    "app.workforce",
])
