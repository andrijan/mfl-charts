# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 14:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_auto_20170310_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='opponent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.Franchise'),
        ),
        migrations.AddField(
            model_name='result',
            name='points',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='franchise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='stats.Franchise'),
        ),
        migrations.AlterField(
            model_name='tradeoffer',
            name='franchise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tradeoffers', to='stats.Franchise'),
        ),
    ]