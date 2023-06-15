# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from mails.models import Contact, EmailTemplate, Mailing, OutgoingEmail
from mails.signals import email_sent


@login_required
def get_templates(request):
    templates = EmailTemplate.objects.all()
    serialized_templates = [{'id': template.id, 'name': template.name} for template in templates]

    return JsonResponse(serialized_templates, safe=False)


@login_required
def get_contacts(request):
    contacts = Contact.objects.all()
    serialized_contact = [{'id': contact.id, 'name': contact.name} for contact in contacts]

    return JsonResponse(serialized_contact, safe=False)


@login_required
def show_mailing_list(request):
    user = request.user
    mailings = Mailing.objects.prefetch_related('recipients').filter(created_by=user)
    context = {
        'mailings': mailings
    }

    return render(request, 'mailing-list.html', context)


@login_required
def show_mailing_details(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)
    outgoing_emails = OutgoingEmail.objects.select_related('mailing').filter(mailing=mailing)
    context = {
        'outgoing_emails': outgoing_emails
    }

    return render(request, 'mailing_details.html', context)


@login_required
@transaction.atomic
def send_mails(request):
    if request.method == 'POST':
        recipient_ids = request.POST.getlist('recipientIds[]')
        template_id = int(request.POST.get('templateSelect'))
        mailing_name = request.POST.get('mailingName')
        delay_hours = int(request.POST.get('delayHours'))

        current_site = get_current_site(request)
        email_template = get_object_or_404(EmailTemplate, id=template_id)

        contacts = Contact.objects.filter(id__in=recipient_ids)

        new_mailing, _ = Mailing.objects.get_or_create(
            name=mailing_name,
            defaults={
                'template': email_template,
                'created_by': request.user,
                'delay_hours': delay_hours
            },
        )

        for contact in contacts:
            new_mailing.recipients.add(contact.id)

            outgoing_email = OutgoingEmail.objects.create(
                mailing=new_mailing,
                recipient_email=contact.email,
                status='created',
            )

            token = outgoing_email.create_token()

            email_content_with_tracking = outgoing_email.render_html_with_tracking(contact, current_site.domain, token)

            outgoing_email.send_email(email_content_with_tracking)

        return JsonResponse({'success': 1})

    return JsonResponse({'error': 0})


@login_required
def check_email_status(request, email_id):
    email = get_object_or_404(OutgoingEmail, id=email_id)
    status = email.status
    response = {'status': status}
    return JsonResponse(response)


@login_required
def track_email_open(request, email_token):
    try:
        email = get_object_or_404(OutgoingEmail, token=email_token)
        email.status = 'opened'
        email.save()
    except OutgoingEmail.DoesNotExist:
        pass
    return HttpResponse(content='', content_type='image/gif')


@receiver(email_sent)
def handle_email_sent(sender, email_id, **kwargs):
    try:
        outgoing_email = get_object_or_404(OutgoingEmail, id=email_id)
        outgoing_email.status = 'sent'
        outgoing_email.save()
    except OutgoingEmail.DoesNotExist:
        pass
