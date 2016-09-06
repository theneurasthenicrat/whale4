# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm, Form, widgets,BaseInlineFormSet
from polls.models import VotingPoll, Candidate, DateCandidate, UNDEFINED_VALUE
from django import forms
import re
from django.core.validators import validate_email
from django.forms import CharField, Textarea
from django.utils.translation import ugettext_lazy as _


class BasePollForm(ModelForm):
    class Meta:
        model = VotingPoll
        fields = ['title','description','closing_date','preference_model','option_choice','option_modify','status','option_shuffle','option_close_poll']
        widgets = {
            'title': widgets.TextInput(attrs={ 'placeholder': _('Enter title')}),
            'closing_date': widgets.DateInput(attrs={'class': 'datepicker','placeholder': _('Enter closing date')}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 4,'placeholder': _('Enter description')}),
            'option_choice': widgets.CheckboxInput(attrs={'data-on-text':_("Yes-option"),'data-off-text':_("No-option")}),
            'option_modify': widgets.CheckboxInput(attrs={'data-on-text': _("Yes-option"),'data-off-text':_("No-option")}),
            'option_shuffle': widgets.CheckboxInput(attrs={'data-on-text': _("Yes-option"),'data-off-text':_("No-option")}),
            'option_close_poll': widgets.CheckboxInput(attrs={'data-on-text': _("Yes-option"),'data-off-text':_("No-option")}),

        }


class VotingPollForm(ModelForm):
    class Meta(BasePollForm.Meta):
        fields = ['title', 'description', 'preference_model']


class OptionForm(ModelForm):
    class Meta(BasePollForm.Meta):
        fields = ['closing_date','option_choice', 'option_modify','option_shuffle']


class PollUpdateForm(ModelForm):
    class Meta(VotingPollForm.Meta):
        fields = ['title', 'description', 'closing_date','option_choice','option_modify','option_shuffle','option_close_poll']


class StatusForm(ModelForm):
    class Meta(BasePollForm.Meta):
        fields = ['status']


class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        exclude = ['poll']
        widgets = {
            'candidate': widgets.TextInput(attrs={'class':'form-control', 'placeholder':_('Candidate')}),

        }
        labels={
            'candidate':"",
        }


class DateCandidateForm(ModelForm):
    class Meta:
        model = DateCandidate
        exclude = ['poll','date']


class DateForm(Form):

    dates = forms.CharField(widget=forms.HiddenInput(),max_length=300)
    candidate = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': ' margin2 form-control'}),required=False,
                                help_text=_('Give a label for the time slot to add (e.g. Morning, 10AM-12AM,...)'),
                                label='')
    def clean_dates(self):
        dates = self.cleaned_data["dates"].split(', ')
        return dates


class NickNameForm(Form):
    def __init__(self, read, *args, **kwargs):
        super(NickNameForm, self).__init__(*args, **kwargs)

        self.fields['nickname'] = forms.CharField(max_length=250, label=_('Nickname *'),widget=forms.TextInput(attrs={ 'placeholder': _('Enter your nickname')}))
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
                self.fields['value' + str(c.id)] = forms.CharField(widget=forms.HiddenInput, error_messages={'required':_('you must order all candidates')})

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if cleaned_data.get('value' + str(c.id)) != str(UNDEFINED_VALUE):
                return
        raise forms.ValidationError(_("You must give a score to at least one candidate!"))


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
    certificate =forms.CharField(max_length=16,widget=forms.TextInput(attrs={ 'placeholder': _('certificate')}))

