# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('candidate', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['candidate'],
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=100, default=uuid.uuid4, editable=False, serialize=False)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(null=True, blank=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('closing_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='VotingScore',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('voter', models.CharField(max_length=30, verbose_name='name')),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DateCandidate',
            fields=[
                ('candidate_ptr', models.OneToOneField(parent_link=True, to='polls.Candidate', auto_created=True, serialize=False, primary_key=True)),
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
                ('poll_ptr', models.OneToOneField(parent_link=True, to='polls.Poll', auto_created=True, serialize=False, primary_key=True)),
                ('preference_model', models.CharField(choices=[('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'), ('Approval', 'Approval Voting (Yes / No)'), ('RankingTies', 'Ranking with ties'), ('Ranking', 'Ranking (no ties)'), ('Numbers#0#10', 'Scores')], default='PositiveNegative', max_length=50)),
                ('poll_type', models.CharField(choices=[('Standard', 'Standard Poll'), ('Date', 'Date Poll')], default='Standard', max_length=20)),
            ],
            bases=('polls.poll',),
        ),
        migrations.AddField(
            model_name='votingscore',
            name='candidate',
            field=models.ForeignKey(to='polls.Candidate'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='poll',
            field=models.ForeignKey(to='polls.VotingPoll', related_name='candidates'),
        ),
    ]
