# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('sealed_ballots', models.BooleanField(default=False)),
                ('choice_idontknow', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(to='polls.VotingPoll')),
            ],
        ),
        migrations.AlterModelOptions(
            name='datecandidate',
            options={'ordering': ['date', 'id']},
        ),
    ]
