# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from datetime import timedelta
from urlparse import urljoin

from django.contrib.auth.models import User
from django.db import models
from django.template import Context, Template
from django.utils.datetime_safe import datetime

from mails.tasks import send_email_task


class EmailTemplate(models.Model):
    name = models.CharField(
        verbose_name='Имя шаблона',
        max_length=254,
    )

    description = models.TextField(
        verbose_name='Описание шаблона',
        blank=True,
    )

    subject = models.CharField(
        verbose_name='Тема письма',
        max_length=254,
        blank=False,
    )

    email_html_text = models.TextField(
        verbose_name='Текст письма html',
        blank=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Шаблон рассылки'
        verbose_name_plural = 'Шаблоны рассылки'


class Contact(models.Model):
    name = models.CharField(
        verbose_name='Имя',
        max_length=254,
    )
    surname = models.CharField(
        verbose_name='Фамилия',
        max_length=254,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
    )
    birthday = models.DateField(
        verbose_name='День рождения',
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'


class Mailing(models.Model):
    name = models.CharField(
        verbose_name='Имя',
        max_length=254,
    )
    template = models.ForeignKey(
        EmailTemplate,
        verbose_name="Шаблон",
        on_delete=models.CASCADE,
        related_name="templates"
    )
    recipients = models.ManyToManyField(
        Contact,
        verbose_name="Получатели",
        related_name="recipients"
    )
    created_by = models.ForeignKey(
        User,
        verbose_name="Кем создана",
        on_delete=models.CASCADE,
        related_name="created_by"
    )
    created_at = models.DateTimeField(auto_now_add=True, )
    delay_hours = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class OutgoingEmail(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создано'),
        ('sent', 'Отправлено'),
        ('opened', 'Открыто'),
    )
    mailing = models.ForeignKey(
        Mailing,
        verbose_name="Рассылка",
        on_delete=models.CASCADE,
        related_name="malings"
    )
    recipient_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=255, blank=True)

    def create_token(self):
        token = str(uuid.uuid4())
        self.token = token
        self.save()

        return token

    def render_html_with_tracking(self, contact, domain, token):
        context = Context({
            'user': contact,
            'domain': domain,
        })

        tracking_pixel_url = urljoin('https://' + domain, '/tracking/' + token)
        email_html_text = self.mailing.template.email_html_text
        email_content_with_tracking = email_html_text + '<img src="' + tracking_pixel_url + ' alt="img opened"">'

        return Template(email_content_with_tracking).render(context)

    def send_email(self, email_content_with_tracking):
        subject = self.mailing.template.subject
        recipient_email = self.recipient_email

        delay_hours = self.mailing.delay_hours
        delay_seconds = int(delay_hours) * 3600
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)

        task_result = send_email_task.apply_async(
            args=[subject, email_content_with_tracking, recipient_email, self.id],
            eta=scheduled_time
        )

        self.task_id = task_result.id
        self.save()

    def __unicode__(self):
        return self.recipient_email

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
