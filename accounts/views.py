# -*- coding: utf-8 -*-

# imports ####################################################################

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.models import User

class register(CreateView):
    template_name = 'accounts/register.html'
    success_url = '/polls/'
    form_class = UserCreationForm
    model = User