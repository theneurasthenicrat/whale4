# -*- coding: utf-8 -*-

# imports ####################################################################

from django import forms
from whale4.models import VotingPoll

# forms ######################################################################

class CreateVotingPollForm(forms.Form):
    title = forms.CharField(max_length=250, required=True, label='Title')
    description = forms.CharField(max_length=800, widget=forms.Textarea(),
                                  label='Description (max. 800 characters)')
    poll_type = forms.ChoiceField(choices = VotingPoll.POLL_TYPES,
                                  required=True, label='Poll type') 
    preference_model = forms.ChoiceField(choices=VotingPoll.PREFERENCE_MODELS,
                                         required=True, label='Preference model')

class AddCandidateForm(forms.Form):
    label = forms.CharField(max_length=50, required=True, label='Label')

    def clean_label(self):
        label = self.cleaned_data["label"]
        return label

class AddDateCandidateForm(forms.Form):
    label = forms.CharField(max_length=50, required=True, label='Label')
    dates = forms.CharField(max_length=300, required=True, label='Dates')

    def clean_label(self):
        label = self.cleaned_data["label"]        
        return label

    def clean_dates(self):
        dates = self.cleaned_data["dates"].split(',')
        return dates


class RemoveCandidateForm(forms.Form):
    number = forms.CharField(max_length=50, required=True, label='Candidate Number')

    def clean_label(self):
        number = self.cleaned_data["number"]
        return number

class RemoveVoterForm(forms.Form):
    voter = forms.CharField(max_length=100, required=True, label='Voter id')

    def clean_label(self):
        id = self.cleaned_data["voter"]
        return id


class VotingForm(forms.Form):
    def __init__(self, candidates, preference_model, voter, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        if not voter:
            self.fields['nickname'] = forms.CharField(max_length=250, required=True, label='Nickname')
        for c in candidates:
            self.fields['score-' + str(c.number)] = forms.ChoiceField(
                choices = [('undefined', "I don't know...")] + list(zip(preference_model.values, preference_model.texts)),
                required=True, label=str(c)
                )
        self.candidates = candidates

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if cleaned_data.get('score-' + str(c.number)) != 'undefined':
                return
        raise forms.ValidationError("You must give a score to at least one candidate!")
            

