from django import forms
from django.forms import widgets
from accounts.models import WhaleUser
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(label=_('Email address *'),widget=forms.EmailInput(attrs={ 'placeholder': _('Enter your email')}), max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': _('Enter your password')}),label=_('Password *'))


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': _('Enter your password'), 'autocomplete': 'new-password'}),label=_('Password *'))
    password_confirmation = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': _('Confirm your password'), 'autocomplete': 'new-password'}),label=_('Password confirmation *'))

    class Meta:
        model = WhaleUser
        fields = ['email', 'nickname']
        widgets = {
            'email': widgets.EmailInput(attrs={'placeholder': _('Enter your email')}),
            'nickname': widgets.Input(attrs={ 'placeholder': _('Enter your nickname')}),

        }

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError(_("Passwords don't match"))
        return password_confirmation

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label=_('Email address'), max_length=255, required=True)
    message = forms.CharField(widget=forms.Textarea)

    def send_email_contact(self):
        data=self.cleaned_data

        send_mail('message from  '+data[ 'name'],data['message'], data['email'],['whale4.ad@gmail.com'],
                   fail_silently=False)
