# -*- coding: utf-8 -*-

# imports ####################################################################

from django import forms
from whale4.models import VotingPoll

# forms ######################################################################

class CreateVotingPollForm(forms.Form):
    title = forms.CharField(max_length=250, required=True, label='Title')
    description = forms.CharField(max_length=800, widget=forms.Textarea(),
                                  label='Description (max. 800 characters)')
    admin_password = forms.CharField(widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=True))

    def clean_confirm_password(self):
        first = self.cleaned_data["admin_password"]
        second = self.cleaned_data["confirm_password"]

        if first != second:
            raise forms.ValidationError("The two passwords should be the same!")

        return second

class AddCandidateForm(forms.Form):
    label = forms.CharField(max_length=50, required=True, label='Label')

    def clean_label(self):
        label = self.cleaned_data["label"]
        
        return label

class VotingForm(forms.Form):
    nickname = forms.CharField(max_length=250, required=True, label='Nickname')

    def __init__(self, candidates, preference_model, params = {}):
        forms.Form.__init__(self, params)
        for c in candidates:
            self.fields['score-' + str(c.number)] = forms.ChoiceField(
                choices = list(zip(preference_model.values, preference_model.texts)),
                required=True, label=c.label
                )
        
                

