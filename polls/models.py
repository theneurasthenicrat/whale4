# -*- coding: utf-8 -*-
import uuid
from datetime import date, timedelta
from django.db import models
from accounts.models import WhaleUser,User
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from accounts.models import WhaleUser

class Poll(PolymorphicModel):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250,verbose_name= _("title *"))
    description = models.TextField(blank=True,null=True,verbose_name= _("description"))
    creation_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(default=date.today()+timedelta(days=1000),verbose_name= _("closing date * "))
    admin = models.ForeignKey(WhaleUser, on_delete=models.CASCADE,related_name='polls')

    def is_closed(self):
        print(self.closing_date)
        print(date.today())
        return self.closing_date <= date.today()


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
    option_blocking_poll=models.BooleanField(default=True,verbose_name=_("blocking option explanation"))

    def candidate_list(self, anonymize=False):
        if anonymize:
            nb_candidates = self.candidates.all().count()
            return ["Candidate #" + str(i) for i in range(1, nb_candidates + 1)]
        if self.poll_type == 'Date':
            return ["{}, {}".format(c.date, c.candidate)
                    for c in DateCandidate.objects.filter(poll_id=self.id)]
        return list(self.candidates.all().values_list("candidate", flat=True))

    def voting_profile(self):
        if self.poll_type == 'Date':
            candidate_indexes = {c.id: index for (index, c) in enumerate(DateCandidate.objects.filter(poll_id=self.id))}
        else:
            candidate_indexes = {c.id: index for (index, c) in enumerate(self.candidates.all())}
        nb_candidates = self.candidates.count()
        if nb_candidates:
            iterator = iter(VotingScore.objects.filter(candidate__poll=self)\
                            .values('voter__id', 'voter__nickname', 'voter__polymorphic_ctype', 'value', 'candidate__id')\
                            .order_by('last_modification', 'candidate'))
            
            content_type = ContentType.objects.get_for_model(WhaleUser).id

            finished = False
            while not finished:
                try:
                    scores = [UNDEFINED_VALUE] * nb_candidates
                    for _ in range(nb_candidates):
                        current = next(iterator)
                        scores[candidate_indexes[current['candidate__id']]] = current['value']

                    yield {
                        'id': current['voter__id'],
                        'nickname': (current['voter__nickname'] if self.ballot_type != 'Secret'
                                     else '(Anonymous)'),
                        'scores': scores,
                        'whaleuser': current['voter__polymorphic_ctype'] == content_type
                    }
                except StopIteration:
                    finished = True

    def nb_voters(self):
        """Returns the number of voters of the poll (performs a DB query)."""
        return VotingScore.objects.filter(candidate__poll=self).values('voter__id').distinct().count()
                
    def voting_profile_matrix(self):
        """Returns the voting profile as a matrix.

        In the matrix returned by the function, each row represents
        a vote, and each column represents a candidate. Each cell
        then contains the value given by a vote to a candidate."""
        matrix = []
        for vote in self.voting_profile():
            matrix.append(vote['scores'])
        return matrix

    def majority_margin_matrix(self):
        """Returns the majority matrix of a profile.

        The value at cell (i, j) is the number of voters that strictly prefer
        candidate i to candidate j."""
        profile = self.voting_profile_matrix()
        nb_candidates = len(profile[0])
#        print(profile)
        if not profile:
            nb_candidates = self.candidates.count()
        matrix = [[0] * nb_candidates for _ in range(nb_candidates)]
        for i in range(nb_candidates):
            for j in range(i + 1, nb_candidates):
                for vect in profile:
                    if vect[i] > vect[j]:
                        matrix[i][j] += 1
                    elif vect[j] > vect[i]:
                        matrix[j][i] += 1
        return matrix

    def __iter__(self, anonymize=False, aggregate=None):
        """Creates an iterator on the poll (serializes the poll as a dictionnary)."""
        candidates = self.candidate_list(anonymize)
        yield 'candidates', candidates
        preference_model = preference_model_from_text(self.preference_model, len(candidates))
        yield 'preferenceModel', preference_model.as_dict_option() if self.option_choice\
            else preference_model.as_dict()
        yield 'type', 1 if self.poll_type == 'Date' else 0
        votes = []
        if not aggregate:
            matrix = self.voting_profile()
            for i, vote in enumerate(matrix):
                votes.append({'name': 'Voter #' + str(i + 1) if anonymize else vote['nickname'],
                              'values': vote['scores']})
            yield 'nbVoters', len(votes)
            yield 'votes', votes
        elif aggregate == 'majority':
            matrix = self.majority_margin_matrix()
            yield 'nbVoters', self.nb_voters()
            yield 'matrix', matrix
        else:
            yield 'votes', 'Unknown aggregation method: ' + aggregate


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
        return zip(self.values[1:], [_(t) for t in self.texts[1:]])

    def zip_preference_option(self):
        return zip(self.values, [_(t) for t in self.texts])

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
        values = [x for x in range(nb_min, nb_max + 1)]
        texts =[str(x) for x in values]
        PreferenceModel.__init__(self, "scores", texts, values)

positiveNegative=PreferenceModel("positiveNegative",
                                 ["--", "-", "0",
                                  "+", "++"],
                                 [-2, -1, 0, 1, 2])

approval=PreferenceModel("approval",
                         ["no", "yes"],
                         [0, 1])

        
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
