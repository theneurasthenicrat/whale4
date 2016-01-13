# -*- coding: utf-8 -*-

# imports ####################################################################

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Max
from whale4.forms import CreateVotingPollForm, AddCandidateForm, RemoveCandidateForm, VotingForm
from whale4.models import VotingPoll, Candidate, User, VotingScore, preference_model_from_text
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password

# decorators #################################################################

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
                'title': "Damned...",
                'message': 'Unknown poll number {0}.'.format(poll_id)
                })
        return fn(request, poll)
    
    return wrapped

def with_admin_rights(fn):
    def wrapped(request, poll):
        referer = request.get_full_path()
        if 'referer' in request.GET:
            referer = request.GET['referer']

        if request.method != 'POST' or "admin_password" not in request.POST:
            return render(request, 'whale4/authenticate-admin.html', {'error': 0, 'referer': referer})

        admin_password = request.POST['admin_password']
        if not check_password(admin_password, poll.admin_password):
            return render(request, 'whale4/authenticate-admin.html', {'error': 1, 'referer': referer})
        return fn(request, poll, admin_password)

    return wrapped


# views ######################################################################

@with_valid_poll
def view_poll(request, poll):
    """Displays a specific poll."""

    success = None
    if 'success' in request.GET:
        if request.GET['success'] == '1':
            success = "Your vote has been added to the poll, thank you!"

    preference_model = preference_model_from_text(poll.preference_model)
    candidates = Candidate.objects.filter(poll_id=poll.id).order_by('number')
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).order_by('voter')
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
                tab[id]['scores'].append(
                    {
                        'value': scores[id][c.number],
                        'class': 'poll-{0:d}percent'.format(int(round(preference_model.evaluate(scores[id][c.number]), 1) * 100)),
                        'text': preference_model.value2text[scores[id][c.number]]
                        }
                    )
            else:
                tab[id]['scores'].append(
                    {
                        'value': 'undefined',
                        'class': 'poll-undefined',
                        'text': 'undefined'
                        }
                    )

    values = None if tab == {} else tab.values()

    return render(request, 'whale4/poll.html', {
        'poll': poll,
        'candidates': candidates,
        'votes': values,
        'success': success}
                  )

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
            admin_password = data['admin_password']
            poll.admin_password = make_password(admin_password, salt='whale4salt')
            poll.preference_model = data['preference_model']

            poll.save()

            success = "<strong>Poll successfully created!</strong> Now add the candidates to the poll..."
            return render(request, 'whale4/manage-candidates.html', {'form': None, 'poll_id': poll.id, 'success': success, 'candidates': [], 'admin_password': admin_password})

    else:
        form = CreateVotingPollForm()

    return render(request, 'whale4/create-voting-poll.html', {'form': form})

@with_valid_poll
@with_admin_rights
def admin_poll(request, poll, admin_password):
    return render(request, 'whale4/admin-poll.html', {'poll_id': poll.id, 'poll': poll, 'admin_password': admin_password})


@with_valid_poll
@with_admin_rights
def manage_candidates(request, poll, admin_password):
    success = None
    form = None
    if 'success' in request.GET:
        if request.GET['success'] == '1':
            success = "Candidate successfully added!"

    # If we are here, we already know that the request method is POST
    # (thanks to admin_rights)
    if 'action' in request.POST and request.POST['action'] == 'add':
        form = AddCandidateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            n = Candidate.objects.filter(poll=poll.id).aggregate(Max('number'))['number__max'] + 1
            
            cand = Candidate.objects.create(
                label = data['label'],
                number = n,
                poll = poll
                )

    if 'action' in request.POST and request.POST['action'] == 'remove':
        form = RemoveCandidateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            n = request.POST['number']
            cand = Candidate.objects.get(
                number = n,
                poll = poll
                )
            cand.delete()

        
    candidates = Candidate.objects.filter(poll_id=poll.id).order_by('number')
    if candidates == []:
        candidates = None

    return render(request, 'whale4/manage-candidates.html', {'form': form, 'poll_id': poll.id, 'success': success, 'candidates': candidates, 'admin_password': admin_password})



@with_valid_poll
def authenticate_admin(request, poll):
    error = None
    if 'referer' not in request.GET: # Redirect to home...
        return redirect('/')
    referer = request.GET['referer']
    
    if 'error' in request.GET:
        if request.GET['error'] == '1':
            error = "<strong>Whoops...</strong><br/>It seems that you have supplied an incorrect administration password for this poll..."

    return render(request, 'whale4/authenticate-admin.html', {'poll_id': poll.id, 'error': error, 'referer': referer})



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

            return redirect('/poll?poll=' + str(poll.id) + '&success=1')

    else:
        form = VotingForm(candidates, preference_model)

    
    return render(request, 'whale4/vote.html', {'form': form, 'poll_id': poll.id})



    
