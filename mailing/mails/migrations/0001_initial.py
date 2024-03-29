# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-06-08 10:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Template name')),
                ('description', models.TextField(blank=True, verbose_name='Template description')),
                ('subject', models.CharField(max_length=254, verbose_name='Subject')),
                ('email_html_text', models.TextField(blank=True, verbose_name='Email html text')),
            ],
        ),
    ]
