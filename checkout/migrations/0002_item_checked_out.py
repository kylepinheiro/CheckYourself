# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-22 18:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='checked_out',
            field=models.BooleanField(default=False),
        ),
    ]
