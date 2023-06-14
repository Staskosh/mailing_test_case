from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(subject, email_content_with_tracking, recipient_email):
    msg = EmailMultiAlternatives(
        subject,
        email_content_with_tracking,
        settings.EMAIL_HOST_USER,
        [recipient_email, ],
    )
    msg.attach_alternative(email_content_with_tracking, "text/html")

    return msg.send()
