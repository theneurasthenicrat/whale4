# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm,BaseFormSet,Form, widgets
from polls.models import VotingPoll,Candidate,DateCandidate
from django import forms

class VotingPollForm(ModelForm):
    class Meta:
        model = VotingPoll
        exclude=['admin']
        widgets = {
            'closing_date': widgets.DateInput(attrs={'class': 'datepicker'}),
        }

    def save(self, user=None):
        voting_poll= super(VotingPollForm, self).save(commit=False)
        if user:
            voting_poll.admin = user
        voting_poll.save()
        return voting_poll

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

class VotingForm(forms.Form):
    def __init__(self, candidates, preference_model, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)
        
        self.fields['nickname'] = forms.CharField(max_length=250, required=True, label='Nickname')
        for c in candidates:
            self.fields['value'+str(c.id)] = forms.ChoiceField(
                choices = [('undefined', "I don't know...")] + list(zip(preference_model.values, preference_model.texts)),
                required=True, label= c
                )
            self.candidates = candidates

            
    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if cleaned_data.get('value'+str(c.id)) != 'undefined':
                return
        raise forms.ValidationError("You must give a score to at least one candidate!")
  
            
