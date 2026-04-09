# tasks.py
# from celery_app import celery
# from email_utils import send_email_flask  # import your reusable function
# import logging

# logger = logging.getLogger(__name__)

# @celery.task(bind=True, max_retries=5, default_retry_delay=60)
# def send_bulk_emails(self, emails):
#     """Send multiple emails asynchronously via Celery."""
#     try:
#         for user in emails:
#             try:
#                 send_email_flask(
#                     to=user["email"],
#                     subject=user["subject"],
#                     html=user["html"],
#                     attachments=user.get("attachments", []),
#                     sender_name=user.get("from_name", "Alice Restaurant")
#                 )
#                 logger.info(f"Sent to {user['email']}")
#             except Exception as e:
#                 logger.error(f"Failed to send to {user['email']}: {e}")

#     except Exception as exc:
#         logger.error(f"Fatal error, retrying: {exc}")
#         raise self.retry(exc=exc)

from celery_app import celery
from email_utils import send_email_flask
import logging, os, mysql.connector
from dotenv import load_dotenv

# Load .env for Celery worker
load_dotenv()

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=5, default_retry_delay=60)
def send_bulk_emails(
    self,
    emails,
    subject_template,
    html_template,
    from_name,
    org,
    sample_size
):
    """
    Sends the entire email batch AND logs one history entry.
    """

    try:
        # ----------------------
        # 1. Send emails
        # ----------------------
        for user in emails:
            try:
                send_email_flask(
                    to=user["email"],
                    subject=user["subject"],
                    html=user["html"],
                    attachments=user.get("attachments", []),
                    sender_name=user.get("from_name", from_name)
                )
                logger.info(f"Sent to {user['email']}")
            except Exception as e:
                logger.error(f"Failed to send to {user['email']}: {e}")

        # ----------------------
        # 2. Save history (one row)
        # ----------------------
        total_sent = len(emails)

        db = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO email_history (org, subject, html, from_name, sample_size, total_sent)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            org,
            subject_template,
            html_template,
            from_name,
            sample_size,
            total_sent
        ))

        db.commit()
        cursor.close()
        db.close()

        logger.info("Email batch logged successfully.")

    except Exception as exc:
        logger.error(f"Fatal error, retrying batch: {exc}")
        raise self.retry(exc=exc)
import requests


def chunk_list(lst, size):
    """Yield chunks of size `size` from list `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def send_sparrow_batch(numbers, message):
    """Send one batch of up to 100 numbers."""
    url = "https://api.sparrowsms.com/v2/sms/"

    payload = {
        "token": os.getenv("SPARROW_TOKEN"),
        "from": os.getenv("SPARROW_SENDER"),
        "to": ", ".join(numbers),
        "text": message
    }

    try:
        r = requests.post(url, data=payload)

        print("response", r.json())
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@celery.task
def send_bulk_sms_task(message, numbers):
    """
    Background task that:
    - takes the final list of numbers
    - chunks them into 100 per request
    - sends to Sparrow
    """
    batch_size = 100
    results = []

    for batch in chunk_list(numbers, batch_size):
        result = send_sparrow_batch(batch, message)
        results.append({
            "batch_size": len(batch),
            "numbers": batch,
            "response": result
        })

    return {
        "total_numbers": len(numbers),
        "total_batches": len(results),
        "batch_results": results
    }
