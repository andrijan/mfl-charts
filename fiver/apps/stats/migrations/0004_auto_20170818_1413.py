# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-18 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_auto_20170630_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='dynasty_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]