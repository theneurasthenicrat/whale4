# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, redirect
from polls.forms import VotingPollForm, CandidateForm, BaseCandidateFormSet, VotingForm
from polls.models import VotingPoll, Candidate, Poll, preference_model_from_text, VotingScore, PreferenceModel,INDEFINED_VALUE
from django.views.generic.edit import CreateView,FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
# decorators #################################################################

def with_valid_poll(fn):
	def wrapped(request):
		if "poll" not in request.GET:
			return render(request, 'whale4/error.html', {'title': "Error", 'message': 'Missing poll id.'})
		poll_id = request.GET['poll']
		try:
			poll = VotingPoll.objects.get(id = poll_id)
		except ObjectDoesNotExist:
			return render(request, 'whale4/error.html', {'title': "Damned...",'message': 'Unknown poll number {0}.'.format(poll_id)})
		return fn(request, poll)
	return wrapped

def with_valid_voter(fn):
	def wrapped(request, poll):
		if "voter" not in request.GET:
			return render(request, 'whale4/error.html', {'title': "Error",'message': 'Missing voter id.'})
		voter_id = request.GET['voter']
		try:
			voter = User.objects.get(id = voter_id)
		except ObjectDoesNotExist:
			return render(request, 'whale4/error.html', {'title': "Damned...",'message': 'Unknown user number {0}.'.format(voter_id)})
		return fn(request, poll, voter)
	return wrapped


def with_admin_rights(fn):
	def wrapped(request, poll):
		next = request.get_full_path()
		if request.user is None or request.user != poll.admin:
			return redirect('/login?next={next}'.format(next=next))
		return fn(request, poll)
	return wrapped


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

	def form_valid(self, form):
		form.save(self.request.user)
		return super(VotingPollCreate, self).form_valid(form)
	
	def get_success_url(self):
		return reverse_lazy(candidateCreate, kwargs={'pk': self.object.pk, })

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(VotingPollCreate, self).dispatch(*args, **kwargs)

def viewPoll(request, pk):

	poll = VotingPoll.objects.get(id=pk)
	candidates = Candidate.objects.filter(poll_id=pk)
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
	preference_model1 = preference_model_from_text(poll.preference_model)


	scores = {}
	for v in votes:
		if v.voter not in scores:
			scores[v.voter] = {}
		scores[v.voter][v.candidate.id]= v.value
	print(scores)
	tab = {}
	for v in votes:
		id = v.voter
		tab[id] = {}
		tab[id]['id'] = id
		tab[id]['nickname'] = v.voter
		tab[id]['scores'] = []
		for c in candidates:
			if c.id in scores[id]:
				a=preference_model1.value2text(scores[id][c.id]) 
				tab[id]['scores'].append({
					'value': scores[id][c.id],
					'text': a if a!= " I don't know" else "?"
					})

	values = None if tab == {} else tab.values()
	
	return render(request, 'polls/viewPoll.html', {'poll': poll,'candidates': candidates,'votes': values})


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
					VotingScore.objects.create(candidate=c, voter=voter, value=data['value'+str(c.id)])
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		form = VotingForm(candidates, preference_model)

	return render(request, 'polls/vote.html', {'form': form, 'poll': poll})

