# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
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
                ('id', models.CharField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True, max_length=100)),
                ('title', models.CharField(max_length=250, verbose_name='tilte')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('closing_date', models.DateField(null=True, verbose_name='closing date', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VotingScore',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('value', models.IntegerField(verbose_name='value')),
            ],
        ),
        migrations.CreateModel(
            name='DateCandidate',
            fields=[
                ('candidate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.Candidate')),
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
                ('poll_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.Poll')),
                ('poll_type', models.CharField(choices=[('Standard', 'Standard Poll'), ('Date', 'Date Poll')], max_length=20, default='Standard', verbose_name='poll type')),
                ('preference_model', models.CharField(choices=[('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'), ('Approval', 'Approval Voting (Yes / No)'), ('RankingTies', 'Ranking with ties'), ('Ranking', 'Ranking (no ties)'), ('Numbers#0#10', 'Scores')], max_length=50, default='PositiveNegative', verbose_name='preference model')),
            ],
            bases=('polls.poll',),
        ),
        migrations.AddField(
            model_name='votingscore',
            name='candidate',
            field=models.ForeignKey(to='polls.Candidate'),
        ),
        migrations.AddField(
            model_name='votingscore',
            name='voter',
            field=models.ForeignKey(verbose_name='voter', to='accounts.User'),
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
