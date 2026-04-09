# test_mail_delay.py
from tasks import send_bulk_emails

emails = [
    {
        "email": "sarajgimba@gmail.com",
        "subject": "Test Email from Celery",
        "html": "<h1>Hello from Celery!</h1>"
    }
]

# Enqueue task asynchronously
result = send_bulk_emails.delay(emails)

print("Task sent to Celery, ID:", result.id)
