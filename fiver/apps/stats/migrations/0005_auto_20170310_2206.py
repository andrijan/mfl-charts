# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 22:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20170308_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draft_year', models.IntegerField()),
                ('draft_round', models.IntegerField()),
                ('current_franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_picks', to='stats.Franchise')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='original_picks', to='stats.Franchise')),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='TradeOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_initiator', models.BooleanField()),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.Franchise')),
                ('picks', models.ManyToManyField(to='stats.Pick')),
                ('players', models.ManyToManyField(to='stats.Player')),
                ('trade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.Trade')),
            ],
        ),
        migrations.AddField(
            model_name='trade',
            name='franchises',
            field=models.ManyToManyField(through='stats.TradeOffer', to='stats.Franchise'),
        ),
    ]