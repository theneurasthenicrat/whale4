# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, redirect
from polls.forms import VotingPollForm, CandidateForm, BaseCandidateFormSet, VotingForm
from polls.models import VotingPoll, Candidate, Poll, preference_model_from_text, VotingScore, PreferenceModel, PositiveNegative
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.forms import formset_factory

# Create your views here.


def home(request):
	return render(request, 'polls/home.html', {})


def candidateCreate(request, pk):
	
	CandidateFormSet = formset_factory(
	    CandidateForm, extra=0, min_num=2, validate_min=True)

	poll = VotingPoll.objects.get(id=pk)

	if request.method == 'POST':

		formset = CandidateFormSet(request.POST)

		if formset.is_valid():

			for form in formset:
				candidate = form.save(commit=False)
				candidate.poll = poll
				candidate.save()

			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		formset = CandidateFormSet()

	return render(request, 'polls/candidate_form.html', {'formset': formset})


class VotingPollCreate(CreateView):
	model = VotingPoll
	form_class = VotingPollForm
	template_name = "polls/votingPoll_form.html"
	
	def get_success_url(self):
		return reverse_lazy(candidateCreate, kwargs={'pk': self.object.pk, })


def viewPoll(request, pk):

	poll = VotingPoll.objects.get(id=pk)
	candidates = Candidate.objects.filter(poll_id=pk)
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
	preference_model = preference_model_from_text(poll.preference_model)
	users=VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()

	scores = {}
	for v in votes:
		if v.voter not in scores:
			scores[v.voter] = [(v.candidate,v.value)]
		else:
			scores[v.voter].append((v.candidate,v.value))
	print(scores)

	
	return render(request, 'polls/viewPoll.html', {'poll': poll,'candidates': candidates,'votes': scores})


def vote(request, pk):
	poll = VotingPoll.objects.get(id=pk)
	candidates = Candidate.objects.filter(poll_id=poll.id)
	preference_model = preference_model_from_text(poll.preference_model)

	if request.method == 'POST':
		form = VotingForm(candidates, preference_model, request.POST)

		if form.is_valid():
			data = form.cleaned_data
			voter = data['nickname']
                    
			for c in candidates:
             
				if data['value' + str(c.id)] != 'undefined':
					VotingScore.objects.create(
                        candidate=c, voter=voter, value=data['value'+str(c.id)])
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		form = VotingForm(candidates, preference_model)

	return render(request, 'polls/vote.html', {'form': form, 'poll': poll})


