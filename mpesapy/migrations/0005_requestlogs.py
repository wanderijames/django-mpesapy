# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-30 12:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesapy', '0004_auto_20170220_0829'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(help_text=b'Request path', max_length=100)),
                ('body', models.TextField(help_text=b'Request body')),
                ('created', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated', models.DateTimeField(blank=True, editable=False, null=True)),
            ],
        ),
    ]
