# -*- coding: utf-8 -*-

# imports ####################################################################

from django.http import HttpResponse
from django.shortcuts import render, redirect
from whale4.forms import CreateVotingPollForm, AddCandidateForm
from whale4.models import VotingPoll, Candidate
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


def view_poll(request, id_poll):
    """Displays a specific poll."""

    text = "You have requested poll number {0}.".format(id_poll)

    return HttpResponse(text)

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


    
