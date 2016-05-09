# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm,BaseFormSet
from polls.models import VotingPoll,Candidate,DateCandidate

class VotingPollForm(ModelForm):
    class Meta:
        model = VotingPoll
        fields= '__all__'
       

class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        exclude=['poll']

class BaseCandidateFormSet(BaseFormSet):
    def clean(self):
        
        if any(self.errors):
        	return
        candidates = []
        for form in self.forms:
            candidate = form.cleaned_data['candidate']
            if candidate in candidates:
  	            raise forms.ValidationError("candidates must be distinct.")
            candidates.append(candidate)
        