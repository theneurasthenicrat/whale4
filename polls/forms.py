# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm, Form, widgets,BaseInlineFormSet
from polls.models import VotingPoll, Candidate, DateCandidate, UNDEFINED_VALUE
from django import forms
import re
from django.core.validators import validate_email
from django.forms import CharField, Textarea, ValidationError
from django.utils.translation import ugettext as _



class VotingPollForm(ModelForm):
    class Meta:
        model = VotingPoll
        exclude = ['admin','poll_type','option_ballots','option_choice','option_modify','option_experimental']
        widgets = {
            'closing_date': widgets.DateInput(attrs={'class': 'datepicker','placeholder': 'Enter closing date'}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 4}),
        }


class VotingPollUpdateForm(ModelForm):
    class Meta(VotingPollForm.Meta):
        exclude = ['admin','poll_type','option_ballots','option_choice','option_modify','preference_model']


class OptionForm(Form):
    option_choice = forms.BooleanField(label='Vote "I don\'t know" is not allowed',required=False,
                                       help_text="Voters can choice i don't know by default."
                                                 " if you want to remove this option check the box")
    option_modify = forms.BooleanField(label="Modify candidates is not allowed",required=False,
                                       help_text="It is impossible to modify the candidates later( add or remove)")


class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        exclude = ['poll']


class DateCandidateForm(ModelForm):
    class Meta:
        model = DateCandidate
        exclude = ['poll','date']


class DateForm(Form):
    dates = forms.CharField(max_length=300, label='Pick one or several dates', required=True,widget=forms.TextInput(attrs={'class': 'datepicker'}))

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

    def add_fields(self, form, index):
        super(BaseCandidateFormSet, self).add_fields(form, index)
        if self.can_delete:
            form.fields['DELETE'] = forms.BooleanField(required=False,label='x')


class NickNameForm(Form):
    def __init__(self, read, *args, **kwargs):
        super(NickNameForm, self).__init__(*args, **kwargs)

        self.fields['nickname'] = forms.CharField(max_length=250)
        if read:
            self.fields['nickname'].widget.attrs['readonly'] = True


class VotingForm(forms.Form):
    def __init__(self, candidates, preference_model,poll, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)
        self.candidates = candidates

        if poll.preference_model != "Ranks#0":
            for c in candidates:
                self.fields['value' + str(c.id)] = forms.ChoiceField(widget=forms.RadioSelect,
                                                                     choices=preference_model.zip_preference() if not poll.option_choice else preference_model.zip_preference_option(),
                                                                     initial=preference_model.first() if not poll.option_choice else preference_model.first_option() ,
                                                                      label=c.candidate)
        else:
            for c in candidates:
                self.fields['value' + str(c.id)] = forms.CharField(widget=forms.HiddenInput, error_messages={'required':'you must order all candidates'})

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if cleaned_data.get('value' + str(c.id)) != str(UNDEFINED_VALUE):
                return
        raise forms.ValidationError("You must give a score to at least one candidate!")


email_separator_re = re.compile(r'[,;\s]+')


class EmailsListField(CharField):

    widget = Textarea

    def clean(self, value):
        super(EmailsListField, self).clean(value)
        emails = email_separator_re.split(value)
        emails = [email for email in emails if email ]

        for email in emails:
           validate_email(email)
        return emails


class InviteForm(forms.Form):
    email = EmailsListField()


class BallotForm(forms.Form):
    certificate =forms.CharField(max_length=16)
