# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-20 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesapy', '0003_auto_20170214_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='register',
            field=models.BooleanField(default=False, help_text=b'Register URL'),
        ),
        migrations.AddField(
            model_name='business',
            name='registered',
            field=models.BooleanField(default=False, help_text=b'Is URL registered'),
        ),
        migrations.AlterField(
            model_name='business',
            name='bnt',
            field=models.CharField(choices=[((b'B2C',), b'B2C'), (b'B2B', b'B2B'), (b'C2BB', b'C2B Paybill'), (b'C2BT', b'C2B Till'), (b'C2BC', b'C2B Checkout')], db_index=True, default=b'C2BB', help_text=b'Business number type', max_length=5),
        ),
        migrations.AlterField(
            model_name='business',
            name='created',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='business',
            name='updated',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
