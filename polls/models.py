# -*- coding: utf-8 -*-
import uuid
from django.db import models



class Poll(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True,blank=True)
    name = models.CharField(max_length=30)

class VotingPoll(Poll):
    PREFERENCE_MODELS = (
        ('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'),
        ('Approval', 'Approval Voting (Yes / No)'),
        ('RankingTies', 'Ranking with ties'),
        ('Ranking', 'Ranking (no ties)'),
        ('Numbers#0#10', 'Scores')
        )
    POLL_TYPES = (
        ('Standard', 'Standard Poll'),
        ('Date', 'Date Poll')
        )
    preference_model = models.CharField(max_length=50,
                                       choices=PREFERENCE_MODELS,
                                       default='PositiveNegative')
    poll_type = models.CharField(max_length=20,
                                       choices=POLL_TYPES,
                                       default='Standard')

class Candidate(models.Model):
    poll = models.ForeignKey(VotingPoll,on_delete=models.CASCADE,related_name='candidates')
    candidate = models.CharField(max_length=50)

    class Meta: 
        ordering=['candidate']


    def __str__(self):
        return str(self.name)

class DateCandidate(Candidate):
    date = models.DateField()

    class Meta: 
        ordering=['date','candidate']


    def __str__(self):
        return str(self.date) + "#" + str(self.name)

class VotingScore(models.Model):
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE)
    voter = models.CharField(max_length=30,verbose_name='name')
    value = models.IntegerField()
