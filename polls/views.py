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

def home(request):
	return render(request, 'polls/home.html', {})

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
				return redirect(reverse_lazy(candidateCreate, kwargs={'pk': poll.id}))
			else:
				return redirect(reverse_lazy(dateCandidateCreate, kwargs={'pk': poll.id}))	
	else:
		form = VotingPollForm()
	return render(request, "polls/votingPoll_form.html", {'form': form})


def candidateCreate(request, pk):
	poll = get_object_or_404(VotingPoll,id=pk)
	CandidateFormSet = formset_factory(
	    CandidateForm, formset=BaseCandidateFormSet,extra=0, min_num=2, validate_min=True)
	
	if request.method == 'POST':
		formset = CandidateFormSet(request.POST)
		if formset.is_valid():
			for form in formset:
				if form.has_changed():
					candidate = form.save(commit=False)
					candidate.poll = poll
					candidate.save()
			messages.success(request,_('Candidates successfully added!'))
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		formset = CandidateFormSet()
	return render(request, 'polls/candidate_form.html', {'formset': formset})


def dateCandidateCreate(request, pk):
	poll = get_object_or_404(VotingPoll,id=pk)
	CandidateFormSet = formset_factory(CandidateForm,extra=1,formset=BaseCandidateFormSet)
	
	if request.method == 'POST':
		form = DateCandidateForm(request.POST)
		formset = CandidateFormSet(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			dates = data['dates']
			if formset.is_valid():
				for form in formset:
					if form.has_changed():
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

def deleteCandidate(request, pk,cand):
	poll = get_object_or_404(VotingPoll,id=pk)
	candidate = get_object_or_404(DateCandidate,id=cand)
	candidate.delete()
	return redirect(reverse_lazy(dateCandidateCreate, kwargs={'pk': poll.id}))

def vote(request, pk):
	poll = get_object_or_404(VotingPoll,id=pk)
	candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
	preference_model = preference_model_from_text(poll.preference_model)
	months = []
	days = []
	if poll.poll_type ==  'Date':
		(days,months)=daysmonth(candidates)

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

	return render(request, 'polls/vote.html', {'form': form, 'poll': poll,'months':months, 'days':days})

def updateVote(request, pk,voter):
	poll = VotingPoll.objects.get(id=pk)
	candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
	preference_model = preference_model_from_text(poll.preference_model)
	voter = User.objects.get(id = voter)
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
	initial = {}
	initial['nickname']=voter.nickname
	for v in votes:
		initial['value'+ str(v.candidate.id)] = v.value
	if request.method == 'POST':
		form = VotingForm(candidates, preference_model, request.POST)

		if form.is_valid():
			data = form.cleaned_data
			voter.nickname=data['nickname']
			voter.save()
			for v in votes:
				v.value=data['value'+str(v.candidate.id)]
				v.save()
			return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	else:
		form = VotingForm(candidates, preference_model,initial = initial)

	return render(request, 'polls/vote.html', {'form': form, 'poll': poll})

def deleteVote(request, pk,voter):
	poll = VotingPoll.objects.get(id=pk)
	voter = User.objects.get(id = voter)
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)

	if request.method == 'POST':
		votes.delete()
		voter.delete()
		return redirect(reverse_lazy(viewPoll, kwargs={'pk': poll.pk}))
	return render(request, 'polls/delete_vote.html', {'voter': voter, 'poll': poll})

def daysmonth(candidates):
	months = []
	days = []
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
	return (days,months)


def viewPoll(request, pk):
	poll = get_object_or_404(VotingPoll,id=pk)
	candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
	votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
	preference_model = preference_model_from_text(poll.preference_model)
	months = []
	days = []
	if poll.poll_type ==  'Date':
		(days,months)=daysmonth(candidates)
	scores = {}
	for v in votes:
		if v.voter.id not in scores:
			scores[v.voter.id] = {}
		scores[v.voter.id][v.candidate.id]= v.value
	
	tab = {}
	for v in votes:
		id = v.voter.id
		tab[id] = {}
		tab[id]['id'] = id
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

