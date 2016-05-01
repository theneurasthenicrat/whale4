# -*- coding: utf-8 -*-

# imports ####################################################################

from django.views.generic import CreateView
from .admin import UserCreationForm
from .models import WhaleUser

# views ######################################################################

class RegistrationView(CreateView):
    template_name = 'accounts/register.html'
    success_url = '/register-success/'
    form_class = UserCreationForm
    model = WhaleUser
    
