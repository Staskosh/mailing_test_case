from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from mails.models import Contact, EmailTemplate, Mailing, OutgoingEmail
from mails.tasks import send_email_task


class EmailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_email_sent(self):
        subject = 'test subject'
        email_content_with_tracking = 'test_content'
        recipient_email = 'test@email.com'

        template = EmailTemplate.objects.create(
            name='test template',
            subject=subject,
            email_html_text=email_content_with_tracking
        )

        contact = Contact.objects.create(
            name='test',
            surname='testov',
            email=recipient_email
        )

        mailing = Mailing.objects.create(
            name='test mailing',
            template=template,
            created_by=self.user,
            delay_hours=0
        )
        mailing.recipients.add(contact)

        outgoing_email = OutgoingEmail.objects.create(
            mailing=mailing,
            recipient_email=recipient_email
        )

        domain = 'test.com'
        token = outgoing_email.create_token()
        email_content_with_tracking = outgoing_email.render_html_with_tracking(contact, domain, token)

        send_email_task(subject, email_content_with_tracking, recipient_email, outgoing_email.id)

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, subject)
        self.assertEqual(sent_email.body, email_content_with_tracking)
        self.assertEqual(sent_email.to, [recipient_email])

        sent_email_model = OutgoingEmail.objects.get(id=outgoing_email.id)
        self.assertEqual(sent_email_model.recipient_email, recipient_email)
        self.assertEqual(sent_email_model.mailing, mailing)
