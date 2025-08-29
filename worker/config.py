import logging

from celery import Celery

from common.services.redis_service import REDIS_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

worker_app = Celery(
    "celery",
    backend=REDIS_URL,
    broker=REDIS_URL,
)
