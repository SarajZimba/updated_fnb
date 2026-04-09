from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# Now these will be populated correctly
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "alicecore",
    broker=redis_url,
    backend=redis_url,
)

# AUTO DISCOVER TASKS FROM THESE MODULES
celery.autodiscover_tasks([
    'tasks',
    'root.flask_routes.sms_outlet',
])

celery.conf.update(
    task_annotations={
        '*': {'rate_limit': '200/s'}
    }
)
