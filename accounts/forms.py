from django import forms
from accounts.models import WhaleUser
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(label=_('email address'), max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput,label=_('password'))


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput,label=_('password'))
    password_confirmation = forms.CharField(widget=forms.PasswordInput,label=_('password confirmation'))

    class Meta:
        model = WhaleUser
        fields = ['email', 'nickname']

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords don't match")
        return password_confirmation

    def save(self, commit=True):
        # type: (object) -> object
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    