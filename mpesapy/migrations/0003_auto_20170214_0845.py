# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-14 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesapy', '0002_auto_20170209_0837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpesabase',
            name='created',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='mpesabase',
            name='updated',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
