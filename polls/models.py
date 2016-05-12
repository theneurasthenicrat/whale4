# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth.models import User


class Poll(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True,blank=True)
    admin = models.ForeignKey(User, related_name='polls')

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
    poll_type = models.CharField(max_length=20,choices=POLL_TYPES,default='Standard')
    preference_model = models.CharField(max_length=50, choices=PREFERENCE_MODELS, default='PositiveNegative')
    

class Candidate(models.Model):
    poll = models.ForeignKey(VotingPoll,on_delete=models.CASCADE,related_name='candidates')
    candidate = models.CharField(max_length=50)

    class Meta: 
        ordering=['id']

    def __str__(self):
        return str(self.candidate)

class DateCandidate(Candidate):
    date = models.DateField()

    class Meta: 
        ordering=['date']


    def __str__(self):
        return str(self.date) + "#" + str(self.candidate)

class VotingScore(models.Model):
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE)
    voter = models.CharField(max_length=30)
    value = models.IntegerField()

#  preference models ########################################################
INDEFINED_VALUE=-222222222

class PreferenceModel:
   
    def __init__(self, id, texts, values):
        self.id = id
        texts.insert(0," I don't know")
        values.insert(0,INDEFINED_VALUE)
        self.texts = texts
        self.values = values
        
    def zipPreference(self): 
        return zip(self.values, self.texts)

    def nb_values(self): 
        return len(values)

    def min(self): 
        return min(self.values[1:])

    def max(self): 
        return max(self.values[1:])

    def text2value(self,text):
        index= self.texts.index(text)
        return self.values[index]

    def value2text(self,value):
        index= self.values.index(value)
        return self.texts[index]

    def evaluate(self, value):
        return (value - self.min()) / (self.max() - self.min())

    def as_dict(self):
        return {"id": self.id,"values": self.values,"texts": self.texts}

class Ranking(PreferenceModel):
    def __init__(self, nb_cand, ties_allowed = 0):
        values = [range(nb_cand + 1)]
        texts = [str(x) for x in values]
        PreferenceModel.__init__(self,"ranking" + ("WithTies" if ties_allowed else "NoTies"),texts,values)

class Numbers(PreferenceModel):
    def __init__(self, nb_min, nb_max):
        values = [  nb_max - x  for x in range(nb_min, nb_max + 1) ]  
        texts =[str(x) for x in values]
        PreferenceModel.__init__(self, "scores", texts, values)

positiveNegative=PreferenceModel("positiveNegative", ["--", "-", "0", "+", "++"], [-2, -1, 0, 1, 2])
approval=PreferenceModel("approval", ["no", "yes"], [0, 1])
        
def preference_model_from_text(desc):
    parts = desc.split('#')
    if parts[0] == "PositiveNegative":
        return positiveNegative
    if parts[0] == "Ranks":
        return Ranking(int(parts[1]), int(parts[2]))
    if parts[0] == "Numbers":
        return Numbers(int(parts[1]), int(parts[2]))
    if parts[0] == "Approval":
        return approval
    raise Exception("Unknown preference model: %s" % desc)
