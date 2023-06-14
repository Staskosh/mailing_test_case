from celery import shared_task

from mails.emails import send_email
from mails.signals import email_sent


@shared_task
def send_email_task(subject, email_content_with_tracking, recipient_email, email_id):
    try:
        email = send_email(subject, email_content_with_tracking, recipient_email)
        email_sent.send(sender=None, email_id=email_id)

        return email
    except Exception as e:
        return str(e)
