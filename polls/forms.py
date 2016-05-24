# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm, Form, widgets,BaseInlineFormSet
from polls.models import VotingPoll, Candidate, DateCandidate, UNDEFINED_VALUE
from django import forms


class VotingPollForm(ModelForm):
    class Meta:
        model = VotingPoll
        exclude = ['admin']
        widgets = {
            'closing_date': widgets.DateInput(attrs={'class': 'datepicker'}),
        }


class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        exclude = ['poll']


class DateCandidateForm(ModelForm):
    class Meta:
        model = DateCandidate
        exclude = ['poll','date']


class DateForm(Form):
    dates = forms.CharField(max_length=300, required=True)

    def clean_dates(self):
        dates = self.cleaned_data["dates"].split(',')
        return dates


class BaseCandidateFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        candidates = []
        for form in self.forms:
            candidate = form.cleaned_data.get("candidate")
            if candidate in candidates:
                raise forms.ValidationError("candidates must be distinct.")
            candidates.append(candidate)


class VotingForm(forms.Form):
    def __init__(self, candidates, preference_model,poll,read, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)

        self.fields['nickname'] = forms.CharField(max_length=250, required=True, label='Nickname')
        if read:
            self.fields['nickname'].widget.attrs['readonly'] = True
        for c in candidates:
            self.fields['value' + str(c.id)] = forms.ChoiceField(widget=forms.RadioSelect,
                                                                 choices=preference_model.zip_preference() if not poll.option_choice else preference_model.zip_preference_option(),
                                                                 initial=preference_model.last(),
                                                                 required=True, label=c.candidate
                                                                 )
            self.candidates = candidates

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if cleaned_data.get('value' + str(c.id)) != str(UNDEFINED_VALUE):
                return
        raise forms.ValidationError("You must give a score to at least one candidate!")
