# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404,render_to_response
from polls.forms import VotingPollForm, CandidateForm, BaseCandidateFormSet, VotingForm,DateCandidateForm
from polls.models import VotingPoll, Candidate, Poll, preference_model_from_text, VotingScore, PreferenceModel,INDEFINED_VALUE,DateCandidate
from django.views.generic.edit import CreateView,FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.template import RequestContext
from accounts.models import User
from django.utils.translation import ugettext_lazy as _
# Create your views here.
# decorators #################################################################

def with_valid_poll(fn): 
	def wrapped(request,poll_id):
		poll = get_object_or_404(VotingPoll,pk = poll_id)
		return fn(request, poll)
	return wrapped

def with_valid_voter(fn):
	def wrapped(request, poll,voter_id):
		voter = get_object_or_404(User,pk = voter_id)
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
			messages.success(request,_('Candidates successfully added!'))
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		formset = CandidateFormSet()

	return render(request, 'polls/candidate_form.html', {'formset': formset})


def dateCandidateCreate(request, pk):
	
	CandidateFormSet = formset_factory(CandidateForm,extra=0, min_num=1, validate_min=True)

	poll = VotingPoll.objects.get(id=pk)

	if request.method == 'POST':
		form = DateCandidateForm(request.POST)
		formset = CandidateFormSet(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			dates = data['dates']
			if formset.is_valid():
				for form in formset:
					label = form.save(commit=False)
					for date in dates:
						candidate = DateCandidate.objects.create(date=date,poll=poll,candidate=label.candidate)
				messages.success(request,_('Candidates successfully added!'))
				return redirect(reverse_lazy(dateCandidateCreate, kwargs={'pk': poll.pk}))
	else:
		formset = CandidateFormSet()
		form = DateCandidateForm()
		candidates =DateCandidate.objects.filter(poll_id=poll.id)

	return render(request, 'polls/dateCandidate_form.html', {'formset': formset, 'form': form,'candidates':candidates,'poll':poll})

@login_required
def votingPollCreate(request):
	if request.method == 'POST':
		form = VotingPollForm(request.POST)
		if form.is_valid():
			poll = form.save(commit=False)
			poll.admin = request.user
			poll.save()
			messages.success(request, _('Poll successfully created! Now add the candidates to the poll...'))
			if poll.poll_type != 'Date':
				return redirect(reverse_lazy(candidateCreate, kwargs={'pk': poll.id, }))
			else:
				return redirect(reverse_lazy(dateCandidateCreate, kwargs={'pk': poll.id, }))	
	else:
		form = VotingPollForm()
	return render(request, "polls/votingPoll_form.html", {'form': form})

def deleteCandidate(request, pk,cand):
	poll = VotingPoll.objects.get(id=pk)
	candidate = DateCandidate.objects.get(id=cand)
	candidate.delete()
	return redirect(reverse_lazy(dateCandidateCreate, kwargs={'pk': poll.id, }))


def viewPoll(request, pk):
	poll = VotingPoll.objects.get(id=pk)
	
	candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
	preference_model = preference_model_from_text(poll.preference_model)
	months = []
	days = []
	if poll.poll_type ==  'Date':
		for c in candidates:
			current_month = c.date.strftime("%y/%m")
			current_day = c.date.strftime("%y/%m/%d")
			if len(months) > 0 and months[-1]["label"] == current_month:
				months[-1]["value"] += 1
			else:
				months += [{"label": current_month, "value": 1}]
			if len(days) > 0  and days[-1]["label"] == current_day:
				days[-1]["value"] += 1
			else:
				days += [{"label": current_day, "value": 1}]

	scores = {}
	for v in votes:
		if v.voter not in scores:
			scores[v.voter] = {}
		scores[v.voter][v.candidate.id]= v.value
	
	tab = {}
	for v in votes:
		id = v.voter
		tab[id] = {}
		tab[id]['nickname'] = v.voter.nickname
		tab[id]['scores'] = []
		for c in candidates:
			if c.id in scores[id]:
				score=scores[id][c.id]
				tab[id]['scores'].append({
					'value': score,
					'class': 'poll-{0:d}percent'.format(int(round(preference_model.evaluate(score), 1) * 100)) if score != INDEFINED_VALUE else 'poll-undefined',
					'text': preference_model.value2text(score) if score != INDEFINED_VALUE else "?"
					})

	values = None if tab == {} else tab.values()
	
	return render(request, 'polls/viewPoll.html', {'poll': poll,'candidates': candidates,'votes': values,'months':months, 'days':days})


def vote(request, pk):
	poll = VotingPoll.objects.get(id=pk)
	candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
	preference_model = preference_model_from_text(poll.preference_model)

	if request.method == 'POST':
		form = VotingForm(candidates, preference_model, request.POST)

		if form.is_valid():
			data = form.cleaned_data
			voter = User.objects.create(nickname=data['nickname'])
			for c in candidates:
					VotingScore.objects.create(candidate=c, voter=voter, value=data['value'+str(c.id)])
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		form = VotingForm(candidates, preference_model)

	return render(request, 'polls/vote.html', {'form': form, 'poll': poll})


def bad_request(request):
	response = render_to_response('polls/400.html', {},context_instance=RequestContext(request))
	response.status_code = 400
	return response

def permission_denied(request):
	response = render_to_response('polls/403.html', {},context_instance=RequestContext(request))
	response.status_code = 403
	return response

def page_not_found(request):
	response = render_to_response('polls/404.html', {},context_instance=RequestContext(request))
	response.status_code = 404
	return response


def server_error(request):
	response = render_to_response('polls/500.html', {},context_instance=RequestContext(request))
	response.status_code = 500
	return response

