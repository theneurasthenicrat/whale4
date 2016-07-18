# -*- coding: utf-8 -*-

# imports ####################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView,FormView
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from accounts.models import WhaleUser
from accounts.forms import UserCreationForm, LoginForm,ContactForm
from polls.models import VotingPoll


class Register(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    model = WhaleUser

    def get_success_url(self):
        messages.success(self.request, _('Your account has been successfully created.'))
        return reverse_lazy('login')


def login_view(request):
    next_url = None
    if request.GET:
        next_url = request.GET['next']
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["email"] 
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password) 
            if user is not None:
                login(request, user)
                messages.success(request, _('You are successfully log in.'))
                if next_url is not None:
                    return redirect(next_url )
                else:
                    return redirect(reverse_lazy('accountPoll', kwargs={'pk': user.id,}))
            else:
                messages.error(request, _('unknown WhaleUser or bad password.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, })


def logout_view(request):
    logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect(reverse('home'))


class ContactView(FormView):
    template_name = 'accounts/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.send_email_contact()
        return super(ContactView, self).form_valid(form)


class WhaleUserDetail(DetailView):

    model = WhaleUser
    template_name = "accounts/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(WhaleUserDetail, self).get_context_data(**kwargs)
        context['poll_list'] = VotingPoll.objects.filter(admin_id= self.kwargs['pk']).order_by('creation_date')
        context['poll_list_voter'] = VotingPoll.objects.filter(candidates__votingscore__voter_id=self.kwargs['pk']).annotate(total=Count('id')).order_by('creation_date')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WhaleUserDetail, self).dispatch(*args, **kwargs)