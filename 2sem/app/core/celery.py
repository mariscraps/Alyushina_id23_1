from celery import Celery
from app.core.config import settings

celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,  # тут очередь задач
    backend=settings.REDIS_URL,  # тут хранятся результаты задач
    include=['app.tasks']  # тут лежат задачи, которые нужно выполнить
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)
