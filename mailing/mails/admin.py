# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from mails.models import Contact, EmailTemplate, Mailing, OutgoingEmail


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subject')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'birthday')


@admin.register(OutgoingEmail)
class OutgoingEmailAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'recipient_email', 'status', 'created_at')


@admin.register(Mailing)
class MailingEmailAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
