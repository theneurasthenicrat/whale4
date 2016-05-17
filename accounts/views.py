# -*- coding: utf-8 -*-

# imports ####################################################################

from django.shortcuts import render, redirect
from accounts.forms import UserCreationForm, LoginForm
from django.views.generic import CreateView
from accounts.models import WhaleUser
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout

class register(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    model = WhaleUser

    def get_success_url(self):
        messages.success(self.request, 'Your account has been successfully created.')
        return reverse_lazy('login')


def login_view(request):
    next = ""
    if request.GET:  
        next = request.GET['next']
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["email"] 
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password) 
            if user is not None:
                login(request, user)
                messages.success(request, 'You are successfully log in.')
                if next != "":
                    return redirect(next)
                else:
                    return redirect(reverse('home'))
            else:
                messages.error(request, 'unknown WhaleUser or bad password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect(reverse('home'))