# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-30 13:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_auto_20170630_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerresult',
            name='available',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='franchiseplayer',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='franchise_player', to='stats.Player'),
        ),
    ]