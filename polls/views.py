# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render,redirect
from polls.forms import VotingPollForm,CandidateForm,BaseCandidateFormSet
from polls.models import VotingPoll,Candidate, Poll
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy,reverse
from django.forms import formset_factory

# Create your views here.
def home(request):
	return render(request,'polls/home.html',{}) 

def candidateCreate(request, pk):
	
	CandidateFormSet=formset_factory(CandidateForm,extra=0,min_num=2, validate_min=True)

	poll = VotingPoll.objects.get(id = pk)

	if request.method=='POST':

		formset=CandidateFormSet(request.POST)

		

		if formset.is_valid():

			for form in formset:
				candidate=form.save(commit=False)
				candidate.poll=poll
				candidate.save()

		
			return redirect(reverse_lazy(viewPoll,kwargs= {'pk':poll.pk}))
	else:
		formset=CandidateFormSet()

	return render(request,'polls/candidate_form.html',{'formset':formset}) 

class VotingPollCreate(CreateView):
	model=VotingPoll
	form_class=VotingPollForm
	template_name="polls/votingPoll_form.html"
	
	def get_success_url(self): 
		return reverse_lazy(candidateCreate,kwargs={'pk':self.object.pk,})

def viewPoll(request,pk):

	poll = VotingPoll.objects.get(id =pk)
	candidates = Candidate.objects.filter(poll_id=poll.id)
	
	return render(request,'polls/viewPoll.html',{'poll':poll,'candidates': candidates}) 

def vote(request,pk): 

	poll = VotingPoll.objects.get(id =pk)
	candidates = Candidate.objects.filter(poll_id=poll.id)

	pollType=poll.poll_type