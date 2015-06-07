# -*- coding: utf-8 -*-

# imports ####################################################################

from django.http import HttpResponse
from django.shortcuts import render, redirect
from whale4.forms import CreateVotingPollForm, AddCandidateForm, VotingForm
from whale4.models import VotingPoll, Candidate, User, VotingScore, preference_model_from_text
from django.core.exceptions import ObjectDoesNotExist

# decora######################################################################

def with_valid_poll(fn):
    def wrapped(request):
        if "poll" not in request.GET:
            return render(request, 'whale4/error.html', {'title': "Error",
                                                         'message': 'Missing poll id.'})
        poll_id = request.GET['poll']
        try:
            poll = VotingPoll.objects.get(id = poll_id)
        except ObjectDoesNotExist:
            return render(request, 'whale4/error.html', {
                'title': "Error",
                'message': 'Unknown poll number {0}.'.format(poll_id)
                })
        return fn(request, poll)
    
    return wrapped


# views ######################################################################

@with_valid_poll
def view_poll(request, poll):
    """Displays a specific poll."""

    candidates = Candidate.objects.filter(poll_id=poll.id).order_by('number')
    votes = VotingScore.objects.filter(candidate__poll__id = 1).order_by('voter')
    scores = {}
    for v in votes:
        if v.voter.id not in scores:
            scores[v.voter.id] = {}
        scores[v.voter.id][v.candidate.number] = v.value
        
    tab = {}
    for v in votes:
        id = v.voter.id
        tab[id] = {}
        tab[id]['nickname'] = v.voter.nickname
        tab[id]['scores'] = []
        for c in candidates:
            if c.number in scores[id]:
                tab[id]['scores'].append(scores[id][c.number])
            else:
                tab[id]['scores'].append('undefined')

    return render(request, 'whale4/poll.html', {'poll': poll, 'candidates': candidates, 'votes': votes, 'tab': tab.values()})

def home(request):
    return render(request, 'whale4/index.html', {})

def create_voting_poll(request):
    if request.method == 'POST':
        form = CreateVotingPollForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            poll = VotingPoll()
            poll.title = data['title']
            poll.description = data['description']
            poll.admin_password = data['admin_password']

            poll.save()

            return redirect('/add-candidate?poll=' + str(poll.id) + '&msg=0')

    else:
        form = CreateVotingPollForm()

    return render(request, 'whale4/create-voting-poll.html', {'form': form})

@with_valid_poll
def add_candidate(request, poll):
    message = ''
    if 'msg' in request.GET:
        if request.GET['msg'] == '0':
            message = "Voting poll successfully created!"
            
    if request.method == 'POST':
        form = AddCandidateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            n = Candidate.objects.filter(poll=poll.id).count()
            cand = Candidate.objects.create(
                label = data['label'],
                number = n,
                poll = poll
                )

            return redirect('/add-candidate?poll=' + str(poll.id) + '')

    else:
        form = AddCandidateForm()

    candidates = Candidate.objects.filter(poll_id=poll.id).order_by('number')
    
    return render(request, 'whale4/add-candidate.html', {'form': form, 'poll_id': poll.id, 'message': message, 'candidates': candidates})

@with_valid_poll
def vote(request, poll):
    candidates = Candidate.objects.filter(poll_id=poll.id).order_by('number')
    preference_model = preference_model_from_text(poll.preference_model)

    if request.method == 'POST':
        form = VotingForm(candidates, preference_model, request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create(
                nickname = data['nickname']
                )
            for c in candidates:
                score = VotingScore.objects.create(
                    candidate = c,
                    voter = user,
                    value = data['score-' + str(c.number)]
                    )

            return redirect('/poll/' + str(poll.id) + '?msg=1')

    else:
        form = VotingForm(candidates, preference_model)

    
    return render(request, 'whale4/vote.html', {'form': form, 'poll_id': poll.id})



    
