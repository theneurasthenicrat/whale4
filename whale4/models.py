# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models


# models #####################################################################

class User(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=50)

class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=800)
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True)
    admin_password = models.CharField(max_length=50)

class VotingPoll(Poll):
    PREFERENCE_MODELS = (
        ('PositiveNegative', 'Positive Negative scale (--, -, 0, +, ++)'),
        ('Approval', 'Approval Voting (Yes / No)'),
        ('RankingTies', 'Ranking with ties'),
        ('Ranking', 'Ranking (no ties)'),
        ('Numbers', 'Scores')
        )
    preference_model = models.CharField(max_length=50,
                                       choices=PREFERENCE_MODELS,
                                       default='PositiveNegative')

class Candidate(models.Model):
    poll = models.ForeignKey(VotingPoll, related_name='candidates')
    label = models.CharField(max_length=50)
    number = models.IntegerField()

class VotingScore(models.Model):
    candidate = models.ForeignKey(Candidate)
    voter = models.ForeignKey(User)
    value = models.IntegerField()


#  preference models ########################################################

class PreferenceModel:
    text2value = {}
    value2text = {}
    
    def __init__(self, texts, values):
        self.texts = texts
        self.values = values
        for (t, v) in zip(texts, values):
            self.text2value[t] = v
            self.value2text[v] = t
        self.min = min(values)
        self.max = max(values)
        self.nb_values = len(values)

class PositiveNegative(PreferenceModel):
    def __init__(self):
        PreferenceModel.__init__(self, ["--", "-", "0", "+", "++"], [-2, -1, 0, 1, 2])

class Ranking(PreferenceModel):
    def __init__(self, nb_cand, ties_allowed = 0):
        texts = list(map(str, range(1, nb_cand + 1)))
        values = list(map(lambda x: nb_cand + 1 - x, range(1, nb_cand + 1)))
        PreferenceModel.__init__(self, texts, values)

class Numbers(PreferenceModel):
    def __init__(self, nb_min, nb_max):
        texts = list(map(lambda x: str(nb_max - x), range(nb_min, nb_max + 1)))
        values = list(map(lambda x: nb_max - x, range(nb_min, nb_max + 1))) 
        PreferenceModel.__init__(self, texts, values)

class Approval(PreferenceModel):
    def __init__(self):
        PreferenceModel.__init__(self, ["no", "yes"], [0, 1])
        
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




