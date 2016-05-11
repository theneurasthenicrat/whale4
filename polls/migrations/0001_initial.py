# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('candidate', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.CharField(serialize=False, editable=False, max_length=100, primary_key=True, default=uuid.uuid4)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(null=True, blank=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('closing_date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VotingScore',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('voter', models.CharField(max_length=30, verbose_name='name')),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DateCandidate',
            fields=[
                ('candidate_ptr', models.OneToOneField(serialize=False, primary_key=True, to='polls.Candidate', parent_link=True, auto_created=True)),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date', 'candidate'],
            },
            bases=('polls.candidate',),
        ),
        migrations.CreateModel(
            name='VotingPoll',
            fields=[
                ('poll_ptr', models.OneToOneField(serialize=False, primary_key=True, to='polls.Poll', parent_link=True, auto_created=True)),
                ('preference_model', models.CharField(max_length=50, default='PositiveNegative', choices=[('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'), ('Approval', 'Approval Voting (Yes / No)'), ('RankingTies', 'Ranking with ties'), ('Ranking', 'Ranking (no ties)'), ('Numbers#0#10', 'Scores')])),
                ('poll_type', models.CharField(max_length=20, default='Standard', choices=[('Standard', 'Standard Poll'), ('Date', 'Date Poll')])),
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
            name='administrator',
            field=models.ForeignKey(related_name='polls', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidate',
            name='poll',
            field=models.ForeignKey(related_name='candidates', to='polls.VotingPoll'),
        ),
    ]
