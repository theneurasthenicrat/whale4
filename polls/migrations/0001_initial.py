# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('candidate', models.CharField(max_length=50, verbose_name='candidate')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.CharField(serialize=False, default=uuid.uuid4, max_length=100, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=250, verbose_name='tilte')),
                ('description', models.TextField(verbose_name='description', blank=True, null=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('closing_date', models.DateField(verbose_name='closing date', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VotingScore',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('voter', models.CharField(max_length=30, verbose_name='voter')),
                ('value', models.IntegerField(verbose_name='value')),
            ],
        ),
        migrations.CreateModel(
            name='DateCandidate',
            fields=[
                ('candidate_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='polls.Candidate')),
                ('date', models.DateField(verbose_name='date')),
            ],
            options={
                'ordering': ['date'],
            },
            bases=('polls.candidate',),
        ),
        migrations.CreateModel(
            name='VotingPoll',
            fields=[
                ('poll_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='polls.Poll')),
                ('poll_type', models.CharField(default='Standard', max_length=20, choices=[('Standard', 'Standard Poll'), ('Date', 'Date Poll')], verbose_name='poll_type')),
                ('preference_model', models.CharField(default='PositiveNegative', max_length=50, choices=[('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'), ('Approval', 'Approval Voting (Yes / No)'), ('RankingTies', 'Ranking with ties'), ('Ranking', 'Ranking (no ties)'), ('Numbers#0#10', 'Scores')], verbose_name='preference_model')),
            ],
            bases=('polls.poll',),
        ),
        migrations.AddField(
            model_name='votingscore',
            name='candidate',
            field=models.ForeignKey(to='polls.Candidate'),
        ),
        migrations.AddField(
            model_name='poll',
            name='admin',
            field=models.ForeignKey(related_name='polls', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidate',
            name='poll',
            field=models.ForeignKey(related_name='candidates', to='polls.VotingPoll'),
        ),
    ]
