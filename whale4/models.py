# -*- coding: utf-8 -*-

# imports ####################################################################

import uuid
from django.db import models


# models #####################################################################

class User(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=50)

class Poll(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=800)
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True)
    admin_password = models.CharField(max_length=100)

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
    poll = models.ForeignKey(VotingPoll, related_name='candidates')
    label = models.CharField(max_length=50)
    number = models.IntegerField()

    def __str__(self):
        return str(self.label)

class DateCandidate(Candidate):
    date = models.DateField()

    def __str__(self):
        return str(self.date) + "#" + str(self.label)


class VotingScore(models.Model):
    candidate = models.ForeignKey(Candidate)
    voter = models.ForeignKey(User)
    value = models.IntegerField()


#  preference models ########################################################

class PreferenceModel:
    text2value = {}
    value2text = {}
    
    def __init__(self, id, texts, values):
        self.id = id
        self.texts = texts
        self.values = values
        for (t, v) in zip(texts, values):
            self.text2value[t] = v
            self.value2text[v] = t
        self.min = min(values)
        self.max = max(values)
        self.nb_values = len(values)

    def evaluate(self, value):
        return (value - self.min) / (self.max - self.min)

    def as_dict(self):
        return {"id": self.id,
                "values": self.values,
                "texts": self.texts}
        
class PositiveNegative(PreferenceModel):
    def __init__(self):
        PreferenceModel.__init__(self, "positiveNegative", ["--", "-", "0", "+", "++"], [-2, -1, 0, 1, 2])

class Ranking(PreferenceModel):
    def __init__(self, nb_cand, ties_allowed = 0):
        texts = list(map(str, range(1, nb_cand + 1)))
        values = list(map(lambda x: nb_cand + 1 - x, range(1, nb_cand + 1)))
        PreferenceModel.__init__(self,
                                 "ranking" + ("WithTies" if ties_allowed else "NoTies"),
                                 texts,
                                 values)

class Numbers(PreferenceModel):
    def __init__(self, nb_min, nb_max):
        texts = list(map(lambda x: str(nb_max - x), range(nb_min, nb_max + 1)))
        values = list(map(lambda x: nb_max - x, range(nb_min, nb_max + 1))) 
        PreferenceModel.__init__(self, "scores", texts, values)

class Approval(PreferenceModel):
    def __init__(self):
        PreferenceModel.__init__(self, "approval", ["no", "yes"], [0, 1])
        
def preference_model_from_text(desc):
    parts = desc.split('#')
    if parts[0] == "PositiveNegative":
        return PositiveNegative()
    if parts[0] == "Ranks":
        return Ranking(int(parts[1]), int(parts[2]))
    if parts[0] == "Numbers":
        return Numbers(int(parts[1]), int(parts[2]))
    if parts[0] == "Approval":
        return Approval()
    raise Exception("Unknown preference model: %s" % desc)





