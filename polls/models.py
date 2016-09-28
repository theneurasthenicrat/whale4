# -*- coding: utf-8 -*-
import uuid
from datetime import date, timedelta
from django.db import models
from accounts.models import WhaleUser,User
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel


class Poll(PolymorphicModel):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250,verbose_name= _("title *"))
    description = models.TextField(blank=True,null=True,verbose_name= _("description"))
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(default=date.today()+timedelta(days=1000),verbose_name= _("closing date * "))
    admin = models.ForeignKey(WhaleUser, on_delete=models.CASCADE,related_name='polls')

    def closing_poll(self):
        return self.closing_date >= date.today()


class VotingPoll(Poll):
    PREFERENCE_MODELS = (
                        ('PositiveNegative', _('Positive Negative scale (--, -, 0, +, ++)')),
                        ('Approval', _('Approval Voting (Yes / No)')),
                        ('Ranks#1', _('Ranking with ties')),
                        ('Ranks#0', _('Ranking (no ties)')),
                        ('Numbers#0#10', _('Scores')) )

    POLL_TYPES = (
                    ('Standard', _('Standard Poll')),
                    ('Date', _('Date Poll')))

    BALLOT_TYPES=(
                    ('Open',_('Open Ballot')),
                    ('Secret',_('Secret Ballot')),
                    ('Experimental',_('Experimental Ballot')))

    poll_type = models.CharField(max_length=20,choices=POLL_TYPES,default='Standard',verbose_name= _("poll type"))
    preference_model = models.CharField(max_length=50, choices=PREFERENCE_MODELS, default='PositiveNegative',verbose_name= _("Preference model * "))
    ballot_type = models.CharField(max_length=50, choices=BALLOT_TYPES, default='Open',verbose_name= _("Ballot Type"))
    option_choice=models.BooleanField(default=True,verbose_name=_("Option choice explanation"))
    option_modify=models.BooleanField(default=True,verbose_name=_("Modify choice explanation"))
    option_shuffle=models.BooleanField(default=False,verbose_name=_("Option shuffle explanation"))
    status_poll=models.BooleanField(default=True,verbose_name=_("Status of poll explanation"))

    def candidate_list(self):
        return self.candidates.all().values_list("candidate", flat=True)

    def voting_profile(self):
        candidates = list(self.candidates.all())
        nb_candidates = len(candidates)
        iterator = iter(VotingScore.objects.filter(candidate__poll=self).order_by('last_modification', 'candidate'))
        finished = False
        while not finished:
            try:
                scores = [UNDEFINED_VALUE] * nb_candidates
                for i, c in enumerate(candidates):
                    current = next(iterator)
                    if current.candidate == c:
                        scores[i] = current.value
                yield {'voter': current.voter, 'scores': scores}
            except StopIteration:
                finished = True

    def voting_profile_matrix(self):
        """Returns the voting profile as a matrix.

        In the matrix returned by the function, each row represents
        a vote, and each column represents a candidate. Each cell
        then contains the value given by a vote to a candidate."""
        matrix = []
        for vote in self.voting_profile():
            matrix.append([vote['scores']])
        return matrix

class Candidate(PolymorphicModel):
    poll = models.ForeignKey(VotingPoll,on_delete=models.CASCADE,related_name='candidates')
    candidate = models.CharField(max_length=50,verbose_name= _('candidate'))

    class Meta: 
        ordering=['id']

    def __str__(self):
        return str(self.candidate)


class DateCandidate(Candidate):
    date = models.DateField(verbose_name= _("date"))

    class Meta: 
        ordering=['date','id']

    def __str__(self):
        return str(self.date) + "#" + str(self.candidate)


class VotingScore(models.Model):
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE)
    voter = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name= _("voter"))
    value = models.IntegerField(verbose_name= _("value"))
    last_modification= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'voter')
        ordering = ['last_modification']

#  preference models ########################################################
UNDEFINED_VALUE=-222222222
UNDEFINED_TEXT="?"

class PreferenceModel:
   
    def __init__(self, id, texts, values):
        self.id = id
        texts.insert(0,UNDEFINED_TEXT)
        values.insert(0, UNDEFINED_VALUE)
        self.texts = texts
        self.values = values

    def zip_preference(self):
        return zip(self.values[1:], self.texts[1:])

    def zip_preference_option(self):
        return zip(self.values, self.texts)

    def last(self):
        return self.values[-1]

    def first(self):
        return self.values[1]

    def first_option(self):
        return self.values[0]

    def nb_values(self): 
        return len(self.values)

    def min(self): 
        return min(self.values[1:])

    def len(self):
        return len(self.values[1:])

    def max(self): 
        return max(self.values[1:])

    def text2value(self,text):
        if text == UNDEFINED_TEXT:
            return UNDEFINED_VALUE
        index= self.texts.index(text)
        return self.values[index]

    def value2text(self,value):
        if value == UNDEFINED_VALUE:
            return UNDEFINED_TEXT
        index= self.values.index(value)
        return self.texts[index]

    def evaluate(self, value):
        return (value - self.min()) / float((self.max() - self.min()))

    def as_dict_option(self):
        return {"id": self.id,"values": self.values,"texts": self.texts}

    def as_dict(self):
        return {"id": self.id, "values": self.values[1:], "texts": self.texts[1:]}


class Ranking(PreferenceModel):
    def __init__(self, ties_allowed, nb_cand ):
        texts = [str(x) for x in range(nb_cand,0,-1 )]
        values = [x for x in range(0,nb_cand )]
        PreferenceModel.__init__(self,"ranking"+ ("WithTies" if ties_allowed == 1 else "NoTies"),texts,values)


class Numbers(PreferenceModel):
    def __init__(self, nb_min, nb_max):
        values = [  nb_max - x  for x in range(nb_min, nb_max + 1) ]  
        texts =[str(x) for x in values]
        PreferenceModel.__init__(self, "scores", texts, values)

positiveNegative=PreferenceModel("positiveNegative", ["--", "-", "0", "+", "++"], [-2, -1, 0, 1, 2])

approval=PreferenceModel("approval", ["no", "yes"], [0, 1])

        
def preference_model_from_text(desc,len_cand):
    parts = desc.split('#')
    if parts[0] == "PositiveNegative":
        return positiveNegative
    if parts[0] == "Ranks":
        return Ranking(int(parts[1]), len_cand)
    if parts[0] == "Numbers":
        return Numbers(int(parts[1]), int(parts[2]))
    if parts[0] == "Approval":
        return approval
    raise Exception("Unknown preference model: %s" % desc)
