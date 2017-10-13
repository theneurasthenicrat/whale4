# -*- coding: utf-8 -*-

import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.safestring import mark_safe
from operator import itemgetter
from datetime import datetime, date
from random import shuffle

from django.db.models import Count

from accounts.models import WhaleUser, WhaleUserAnonymous, User, UserAnonymous
from polls.forms import VotingPollForm, CandidateForm,  VotingForm,  DateForm, \
    OptionForm, InviteForm, BallotForm, NickNameForm, StatusForm, PollUpdateForm
from polls.models import VotingPoll, Candidate, preference_model_from_text, VotingScore, UNDEFINED_VALUE, \
    DateCandidate

from polls.utils import days_months, voters_undefined, scoring_method,\
    condorcet_method, runoff_method, randomized_method

from whale4.settings import BASE_URL, EMAIL_FROM

# decorators ###################################################################


def with_valid_poll(init_fn):
    """This decorator transforms a poll_id into an
    actual poll object (or returns a 404 error if such
    a poll does not exist)..."""
    def _wrapped(request, poll_id, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=poll_id)
        return init_fn(request, poll, *args, **kwargs)
    return _wrapped

def with_admin_rights(init_fn):
    """This decorator checks whether the request.user has administration
    rights on the poll.

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, *args, **kwargs):
        if request.user is None or request.user != poll.admin:
            messages.error(request, mark_safe(_("you are not the poll administrator")))
            return redirect(reverse_lazy('redirectPage'))
        return init_fn(request, poll, *args, **kwargs)
    return _wrapped

def with_voter_rights(init_fn):
    """This decorator transforms a voter_id into an
    actual voter object (or returns a 404 error if such
    a voter does not exist)...

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, voter_id, *args, **kwargs):
        voter = get_object_or_404(User, id=voter_id)
        if poll.ballot_type == "Experimental":
            messages.error(request, mark_safe(_('Experimental vote can not be updated')))
            return redirect(reverse_lazy(view_poll, args=(poll.id, )))
        if poll.ballot_type == "Secret":
            if "user" in request.session and request.session["user"] == voter.id:
                return init_fn(request, poll, voter, *args, **kwargs)
            else:
                messages.error(request, mark_safe(_('This is not your vote')))
                return redirect(reverse_lazy(view_poll, args=(poll.id, )))

        if not (isinstance(voter, WhaleUser)) or\
           (request.user is not None and request.user.id == voter.id):
            return init_fn(request, poll, voter, *args, **kwargs)
        else:
            messages.error(request, mark_safe(_('This is not your vote')))
            return redirect(reverse_lazy(view_poll, args=(poll.id, )))

    return _wrapped

def with_viewing_rights(init_fn):
    """This decorator enriches a function by performing
    an initial check to determine whether the user
    has the right to see the requested poll.

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, *args, **kwargs):
        if poll.ballot_type == "Experimental"\
           and (not request.user or request.user != poll.admin):
            messages.error(request, mark_safe(_("you are not the poll administrator")))
            return redirect(reverse_lazy('redirectPage'))
        elif poll.ballot_type == "Secret" and not poll.is_closed():
            messages.error(request, mark_safe(_("The poll is not closed")))
            return redirect(reverse_lazy('redirectPage'))
        return init_fn(request, poll, *args, **kwargs)

    return _wrapped


def certificate_required(init_fn):
    """This decorator enriches a function by performing
    an initial check to determine whether a certificate
    is required and not provided.

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, *args, **kwargs):
        path = request.get_full_path()
        if poll.ballot_type == "Secret" and "user" not in request.session:
            return redirect("{url}?next={path}".format(
                url=reverse_lazy(certificate, kwargs={'pk': poll.id}),
                path=str(path)))
        return init_fn(request, poll, *args, **kwargs)
    return _wrapped


def status_required(init_fn):
    """This decorator enriches a function by performing
    an initial check to determine whether a poll is currently
    blocked or not (concerns experimental polls).

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, *args, **kwargs):
        if poll.ballot_type == "Experimental" and\
           (poll.option_blocking_poll and not poll.status_poll):
            messages.error(request, mark_safe(_("the poll is blocked")))
            return redirect(reverse_lazy('redirectPage'))
        return init_fn(request, poll, *args, **kwargs)
    return _wrapped


def minimum_candidates_required(init_fn):
    """This decorator checks whether there are enough candidates
    in the poll (at least 2). Otherwise it returns an error.

    The decorator assumes that a valid poll has been
    specified as first argument..."""
    def _wrapped(request, poll, *args, **kwargs):
        candidates = Candidate.objects.filter(poll_id=poll.id)
        if candidates.count() < 2:
            messages.error(request, mark_safe(_('You must add at least two candidates')))
            return redirect(reverse_lazy(manage_candidate, args=(poll.id, )))
        return init_fn(request, poll, *args, **kwargs)
    return _wrapped


# default view pages ###########################################################

def bad_request(request):
    """Returns the default page displayed for a bad HTTP request."""
    return render(request, 'polls/error.html', status=400)

def permission_denied(request):
    """Returns the default page displayed for a permission denied error."""
    return render(request, 'polls/error.html', status=403)

def page_not_found(request):
    """Returns the default page displayed for a page not found error."""
    return render(request, 'polls/error.html', status=404)

def server_error(request):
    """Returns the default page displayed for a server error."""
    return render(request, 'polls/error.html', status=500)

def home(request):
    """Returns the home page."""
    return render(request, 'polls/home.html')

def redirect_page(request):
    """Goes to the redirect page (almost empty template)."""
    return render(request, 'polls/redirectPage.html')


# Poll creation views ##########################################################

@login_required
def choose_poll_type(request): ################################### PAGE 0
    """Renders the first page for a poll creation.
    This page asks for the poll type to create
    (classic, date, experimental...)."""
    request.session["update"] = 0
    return render(request, 'polls/new_poll.html')

@login_required
def new_poll(request, choice): ################################### PAGE 1
    """Renders the very first poll creation page.
    Concerns general parameters. Also works for poll update."""
    form = VotingPollForm()
    # I am not sure update is really necessary here
    # I leave that for the moment, but it should be checked...
    if "update" in request.session:
        update_poll = int(request.session["update"]) != 1

    if request.method == 'POST':
        form = VotingPollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.admin = request.user
            if int(choice) == 21:
                poll.poll_type = 'Date'
            if int(choice) == 22:
                poll.ballot_type = 'Secret'
            if int(choice) == 23:
                poll.ballot_type = 'Experimental'

            poll.save()
            messages.success(request, mark_safe(_('General parameters successfully created!')))
            return redirect(reverse_lazy(manage_candidate, args=(poll.pk, )))
    return render(request, 'polls/parameters_poll.html', {
        'form': form,
        'update_poll': update_poll
    })

@login_required
@with_valid_poll
@with_admin_rights
def update_voting_poll(request, poll): ########################### PAGE 1
    """Renders the general parameters options configuration
    page for poll update."""
    update_poll = True
    # I am not sure update is really necessary here
    # I leave that for the moment, but it should be checked...
    if "update" in request.session:
        update_poll = int(request.session["update"]) != 1

    # Really necessary ?
    form = VotingPollForm(instance=poll) if update_poll else PollUpdateForm(instance=poll)

    if request.method == 'POST':
        form = VotingPollForm(request.POST, instance=poll) if update_poll\
               else PollUpdateForm(request.POST, instance=poll)
        if form.is_valid():
            poll = form.save(commit=False)
            if not update_poll:
                close_now_option = form.cleaned_data['close_now']
                if close_now_option:
                    poll.closing_date = date.today()
            poll.save()
            if update_poll:
                messages.success(request, mark_safe(_('General parameters successfully updated!')))
                return redirect(reverse_lazy(manage_candidate, args=(poll.pk, )))
            else:
                messages.success(request, mark_safe(_('Parameters are successfully updated!')))
                return redirect(reverse_lazy(admin_poll, args=(poll.pk, )))
    return render(request, 'polls/parameters_poll.html', locals())


@login_required
@with_valid_poll
@with_admin_rights
@minimum_candidates_required
def advanced_parameters(request, poll):  ######################### PAGE 3
    """Renders the advanced parameters option page."""
    form = OptionForm(instance=poll)
    if request.method == 'POST':
        form = OptionForm(request.POST, instance=poll)
        if form.is_valid():
            poll = form.save()
            messages.success(request, mark_safe(_('Options are successfully added!')))
            return redirect(reverse_lazy(invitation, args=(poll.id, )))
    return render(request, 'polls/option.html', locals())

@login_required
@with_valid_poll
@with_admin_rights
def invitation(request, poll): ################################### PAGE 4
    """Renders the very last poll creation page.
    This page is mostly dedicated to the invitation of voters."""
    update_poll = "update" in request.session and int(request.session["update"]) != 1
    invited_voters = None if poll.ballot_type != "Secret"\
                     else WhaleUserAnonymous.objects.filter(poll=poll.id)
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            for email in form.cleaned_data['email']:
                certi = WhaleUserAnonymous.id_generator()
                WhaleUserAnonymous.objects.create(
                    nickname=WhaleUserAnonymous.nickname_generator(poll.id),
                    email=email,
                    certificate=WhaleUserAnonymous.encodeAES(certi),
                    poll=poll
                )
                subject = '[Whale4] Invitation to participate in election #' + str(poll.pk)
                htmly = get_template('polls/email.html')
                url = BASE_URL + reverse_lazy("vote", args=(str(poll.pk), ))
                data = {'poll': poll, 'certi': certi, 'url': url}
                txt_content = (
                    _('Email text template with url %(url)s and certificate %(certi)s.')
                ) % data
                html_content = htmly.render(Context(data))
                msg = EmailMultiAlternatives(subject, txt_content, EMAIL_FROM, [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            messages.success(request, mark_safe(_('Invited voters successfully added!')))
            return redirect(reverse_lazy(invitation, args=(poll.id, )))
    else:
        form = InviteForm()
    return render(request, 'polls/invite.html', {
        'update_poll': update_poll,
        'invited_voters': invited_voters,
        'form': form,
        'poll': poll
    })


# Candidate management (PAGE 2) ################################################

@login_required
@with_valid_poll
@with_admin_rights
def manage_candidate(request, poll):
    """The main entry point for candidate managements. Basically redirects
    to the relevant page (date or normal) or displays an error message if
    adding or removing candidates is not allowed."""
    if poll.option_modify:
        if poll.poll_type != 'Date':
            return redirect(reverse_lazy(candidate_create, args=(poll.id, )))
        else:
            return redirect(reverse_lazy(date_candidate_create, args=(poll.id, )))
    else:
        messages.error(request, mark_safe(_('Add or remove candidates is not allowed!')))
        return redirect(reverse_lazy('redirectPage'))


@login_required
@with_valid_poll
@with_admin_rights
def candidate_create(request, poll):
    """Manage candidates for a classical poll."""
    candidates = Candidate.objects.filter(poll_id=poll.id)
    form = CandidateForm()

    update_poll = "update" in request.session and int(request.session["update"]) != 1

    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.poll = poll
            if any(str(c) == str(candidate) for c in candidates):
                messages.error(request,
                               mark_safe(_('Candidates must be distinct (%(c)s)')
                                         % {'c': candidate.candidate}))
            else:
                candidate.save()
                voters_undefined(poll)
                messages.success(request,
                                 mark_safe(_('Candidate %(c)s successfully added!')
                                           % {'c': candidate.candidate}))
        return redirect(reverse_lazy(candidate_create, args=(poll.pk, )))
    return render(request, 'polls/candidate.html', {
        'form': form,
        'poll': poll,
        'update_poll': update_poll,
        'candidates': candidates
    })


@login_required
@with_valid_poll
@with_admin_rights
def date_candidate_create(request, poll):
    """Manage candidates for a date poll."""
    candidates = DateCandidate.objects.filter(poll_id=poll.id)
    form = DateForm()

    update_poll = "update" in request.session and int(request.session["update"]) != 1

    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            label = form.cleaned_data['candidate']
            nb_added = 0
            for cand_date in dates:
                candidate = DateCandidate()
                candidate.poll = poll
                candidate.date = cand_date
                candidate.candidate = label
                if any(str(c.date) == str(cand_date)
                       and str(c) == str(candidate.candidate) for c in candidates):
                    messages.error(request, mark_safe(_('Candidates must be distinct (%(c)s)')
                                                      % {'c': candidate.candidate}))
                else:
                    candidate.save()
                    voters_undefined(poll)
                    nb_added += 1
            if nb_added > 0:
                messages.success(request, mark_safe(_('Candidates are successfully added!')))
            return redirect(reverse_lazy(date_candidate_create, args=(poll.pk, )))

    return render(request, 'polls/date_candidate.html', {
        'form': form,
        'poll': poll,
        'update_poll': update_poll,
        'candidates': candidates
    })


@login_required
@with_valid_poll
@with_admin_rights
def delete_candidate(request, poll, cand_id):
    """Delete a candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)
    candidate.delete()
    messages.success(request, mark_safe(_('Candidate has been deleted (%(c)s)!')
                                        % {'c': candidate.candidate}))
    return redirect(reverse_lazy(manage_candidate, args=(poll.id, )))

# Poll administration views ####################################################

@login_required
@with_valid_poll
@with_admin_rights
@minimum_candidates_required
def admin_poll(request, poll):
    """Renders the main poll administration page."""
    request.session["update"] = 1
    return render(request, 'polls/admin.html', {'poll': poll})

@login_required
@with_valid_poll
@with_admin_rights
def reset_poll(request, poll):
    """Resets a poll (deletes all the votes). Be careful with this
    function..."""
    VotingScore.objects.filter(candidate__poll__id=poll.id).delete()
    messages.success(request, mark_safe(_('Poll successfully reset.')))
    return render(request, 'polls/admin.html', {'poll': poll})

@login_required
@with_valid_poll
@with_admin_rights
def delete_poll(request, poll):
    """Deletes a poll and all the votes and candidates in cascade.
    Be careful with this function..."""
    admin = request.user.id
    poll.delete()
    messages.success(request, mark_safe(_('Your poll has been deleted!')))
    return redirect(reverse_lazy('accountPoll', args=(admin, )))

@login_required
@with_valid_poll
@with_viewing_rights
def status(request, poll):
    """Renders the page dedicated to the status of an experimental
    poll (blocked, ready...). Not sure this page is really useful
    in the end..."""
    form = StatusForm(instance=poll)
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=poll)
        if form.is_valid():
            poll = form.save()
            messages.success(request, mark_safe(_('Status is successfully changed!')))
            return redirect(reverse_lazy(admin_poll, args=(poll.id, )))
    return render(request, 'polls/status_poll.html', {'poll': poll, 'form': form})

@login_required
@with_valid_poll
@with_admin_rights
def delete_anonymous(request, poll, voter_id):
    voter = get_object_or_404(WhaleUserAnonymous, id=voter_id)
    if "user" in request.session:
        del request.session["user"]
    voter.delete()
    messages.success(request, mark_safe(_('anonymous voter has been deleted!')))
    return redirect(reverse_lazy(invitation, args=(poll.pk, )))


@with_valid_poll
def certificate(request, poll):
    next_url = None
    if request.GET:
        next_url = request.GET['next']

    form = BallotForm()
    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            certificate = WhaleUserAnonymous.encodeAES(form.cleaned_data['certificate'])
            try:
                user= WhaleUserAnonymous.objects.get(poll=poll.id, certificate=certificate)
                messages.success(request,  mark_safe(_('your certificate is correct')))
                request.session["user"] = str( user.id)
                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect(reverse_lazy('redirectPage'))

            except:
                messages.error (request,  mark_safe(_('your certificate is incorrect')))
                return redirect(reverse_lazy('certificate', args=(poll.id, )))

    return render(request, 'polls/certificate.html', locals())


# vote modification (create/update/delete) #####################################

@with_valid_poll
@certificate_required
@status_required
def vote(request, poll):
    """This function creates a new vote.

    Arguments:
    - the originating HTTP request
    - the poll concerned
    - the voter concerned"""

    if poll.is_closed():
        messages.error(request, mark_safe(_('poll closed, you cannot vote anymore')))
        return redirect(reverse_lazy(view_poll, args=(poll.id, )))

    # First we get all the objects we need:
    # list of candidates, preference model, scores given by the voter
    candidates = DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'\
                 else poll.candidates.all()
#    candidates = Candidate.objects.filter(poll_id=poll.id)
    if poll.option_shuffle:
        candidates = list(candidates)
        shuffle(candidates)
    preference_model = preference_model_from_text(poll.preference_model, len(candidates))

    # This variable determines whether the nickname can be set or not
    read_only_nickname = True
    # Here we will get the voter or create a new one
    voter = None
    if poll.ballot_type == "Secret":
        voter = get_object_or_404(WhaleUserAnonymous, id=request.session["user"])
    else:
        if poll.ballot_type == "Experimental":
            voter = UserAnonymous(nickname=UserAnonymous.nickname_generator(poll.id), poll=poll)
        elif request.user.is_authenticated():
            voter = request.user
        else:
            read_only_nickname = False
            voter = User()

    scores = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    if scores:
        messages.info(request,
                      mark_safe(_('you have already voted, now you can update your vote')))
        return redirect(reverse_lazy(update_vote, args=[poll.id, voter.id]))

    # The two forms in the page (nickname, voting form)
    voting_form, nickname_form = None, None

    # If some data has already been posted, we need:
    # - to check for errors
    # - to update the voter's scores
    if request.method == 'POST':
        if poll.ballot_type == "Secret" and "user" in request.session:
            del request.session["user"]
        voting_form = VotingForm(candidates, preference_model, poll, request.POST)
        nickname_form = NickNameForm(read_only_nickname, request.POST)

        if voting_form.is_valid() and nickname_form.is_valid():
            voter.nickname = nickname_form.cleaned_data['nickname']
            voter.save()
            today = datetime.now()
            for candidate in candidates:
                VotingScore.objects.create(
                    candidate=candidate,
                    last_modification=today,
                    voter=voter,
                    value=voting_form.cleaned_data['value' + str(candidate.id)]
                )
            messages.success(request,
                             mark_safe(_('Your vote has been added to the poll, thank you!')))
            if poll.ballot_type == "Secret":
                return redirect(reverse_lazy(
                    view_poll_secret,
                    args=(poll.pk, ),
                    kwargs={'voter':voter.id}
                ))
            else:
                if poll.ballot_type == "Experimental" and poll.option_blocking_poll:
                    poll.status_poll = False
                    poll.save()
                return redirect(reverse_lazy(view_poll, args=(poll.pk, )))
    else: # a GET request...
        voting_form = VotingForm(candidates, preference_model, poll)
        nickname_form = NickNameForm(read_only_nickname, initial={'nickname': voter.nickname})

    days, months = days_months(candidates) if poll.poll_type == 'Date' else ([], [])

    return render(request, 'polls/vote.html', {
        'poll': poll,
        'candidates': candidates,
        'votingform': voting_form,
        'nicknameform': nickname_form,
        'days': days,
        'months': months
    })

@with_valid_poll
@certificate_required
@with_voter_rights
def update_vote(request, poll, voter):
    """This function modifies an existing vote.

    Arguments:
    - the originating HTTP request
    - the poll concerned
    - the voter concerned"""

    # First we get all the objects we need:
    # list of candidates, preference model, scores given by the voter
    candidates = DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'\
                 else poll.candidates.all()
    if poll.option_shuffle:
        candidates = list(candidates)
        shuffle(candidates)
    preference_model = preference_model_from_text(poll.preference_model, len(candidates))
    scores = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)

    # Creates the dictionnary of initial values
    # Corresponding to previous votes
    initial = {'value' + str(score.candidate.id): score.value for score in scores}

    # This variable determines whether the nickname can be set or not
    read_only_nickname = poll.ballot_type == "Secret" or request.user.is_authenticated()

    # The two forms in the page (nickname, voting form)
    voting_form = VotingForm(candidates, preference_model, poll, initial=initial)
    nickname_form = NickNameForm(read_only_nickname, initial={'nickname': voter.nickname})

    # If some data has already been posted, we need:
    # - to check for errors
    # - to update the voter's scores
    if request.method == 'POST':
        voting_form = VotingForm(candidates, preference_model, poll, request.POST)
        nickname_form = NickNameForm(read_only_nickname, request.POST)
        if poll.ballot_type == "Secret" and "user" in request.session:
            del request.session["user"]
        if voting_form.is_valid() and nickname_form.is_valid():
            data = voting_form.cleaned_data
            voter.nickname = nickname_form.cleaned_data['nickname']
            voter.save()
            for score in scores:
                score.value = data['value' + str(score.candidate.id)]
                score.last_modification = datetime.now()
                score.save()
            messages.success(request, mark_safe(_('Your vote has been updated, thank you!')))
            if poll.ballot_type == "Secret":
                return redirect(reverse_lazy(
                    view_poll_secret,
                    args=(poll.pk, ),
                    kwargs={'voter': voter.id}
                ))
            else:
                return redirect(reverse_lazy(view_poll, args=(poll.pk, )))

    days, months = days_months(candidates) if poll.poll_type == 'Date' else ([], [])

    return render(request, 'polls/vote.html', {
        'poll': poll,
        'candidates': candidates,
        'votingform': voting_form,
        'nicknameform': nickname_form,
        'days': days,
        'months': months
    })


@with_valid_poll
@certificate_required
@with_voter_rights
def delete_vote(request, poll, voter):
    """This function deletes an existing vote.

    Arguments:
    - the originating HTTP request
    - the poll concerned
    - the voter concerned"""

    # First we get the scores associated to the voter...
    scores = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    # ...And delete them
    scores.delete()
    if poll.ballot_type == "Secret":
        del request.session["user"]
    messages.success(request, mark_safe(_('Your vote has been deleted!')))
    # Then we redirect to the poll view page...
    if poll.ballot_type == "Secret":
        return redirect(reverse_lazy(view_poll_secret,
                                     args=(poll.pk, ),
                                     kwargs={'voter': voter.id}))
    else:
        return redirect(reverse_lazy(view_poll, args=(poll.pk, )))


# different views on the polls #################################################


@with_valid_poll
@with_viewing_rights
def view_poll(request, poll):
    if "format" in request.GET:
        if request.GET['format'] == 'json':
            return _view_poll_as_json(poll)
        if request.GET['format'] == 'csv':
            return _view_poll_as_csv(poll)
        if request.GET['format'] == 'preflib':
            return _view_poll_as_preflib(poll)

    if "aggregate" in request.GET:
        return _view_poll_as_json(poll, aggregate=request.GET['aggregate'])
            
        
    is_closed = poll.is_closed()
    candidates = DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'\
                 else poll.candidates.all()
    profile = poll.voting_profile()
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))

    enhanced_profile = [
        {
            'scores': [
                {'value': s,
                 'class': 'poll-{0:d}percent'.format(
                     int(round(preference_model.evaluate(s),
                               1) * 100)) if s != UNDEFINED_VALUE else 'poll-undefined',
                 'text': preference_model.value2text(s)}
                for s in vote['scores']
            ],
            'id': vote['id'],
            'nickname': vote['nickname'],
            'modify': (not vote['whaleuser'] or (request.user is not None and request.user.id == vote['id']))
        }
        for vote in profile]

    days, months = [], []
    if poll.poll_type == 'Date':
        days, months = days_months(candidates)

    return render(request, 'polls/view_poll.html', {
        'poll': poll,
        'candidates': candidates,
        'votes': enhanced_profile,
        'days': days,
        'months': months,
        'is_closed': is_closed,
        'col_width': 85 if not candidates else int(85 / len(candidates))
    })


def view_poll_secret(request, pk ,voter):

    poll = get_object_or_404(VotingPoll, id=pk)
    voter = get_object_or_404(User, id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id).order_by('candidate')
    candidates = Candidate.objects.filter(poll_id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))
    tab = []
    for v in votes:
        score = v.value
        tab.append({
            'value': score,
            'class': 'poll-{0:d}percent'.format(int(round(preference_model.evaluate(score),
                                                          1) * 100)) if score != UNDEFINED_VALUE else 'poll-undefined',
            'text': preference_model.value2text(score) if score != UNDEFINED_VALUE else "?"

        })

    return render(request, 'polls/secret_view.html',locals() )



def _view_poll_as_json(poll, aggregate=None):
    return HttpResponse(json.dumps(dict(poll.__iter__(aggregate=aggregate)), indent=4, sort_keys=True),
                        content_type="application/json")

def _view_poll_as_csv(poll):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="poll-{id}.csv"'.format(id=poll.id)
    response.write(',')
    response.write(','.join([str(c) for c in poll.candidate_list()]))
    response.write('\n')
    for vote in poll.voting_profile():
        response.write(vote['nickname'] + ',')
        response.write(','.join([str(s) for s in vote['scores']]))
        response.write('\n')
    return response


def _view_poll_as_preflib(poll):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="poll-{id}.soc"'.format(id=poll.id)
    poll_dict = dict(poll)
    response.write(str(len(poll_dict['candidates'])) + '\n')
    for i, c in enumerate(poll_dict['candidates']):
        response.write('{n},{l}\n'.format(n=i+1, l=str(c)))
    nb_votes = len(poll_dict['votes'])
    response.write('{a},{b},{c}\n'.format(a=nb_votes, b=nb_votes, c=nb_votes))

    for v in poll_dict['votes']:
        response.write('1,')
        order = sorted(enumerate(v['values']), key=lambda x: x[1], reverse=True)
        response.write(','.join((str(x[0] + 1) for x in order)))
        response.write('\n')

    return response


@with_valid_poll
def result_all(request, poll):
    return render(request, 'polls/all_result.html', locals())

@with_valid_poll
def result_view(request, poll, method):
    #poll = get_object_or_404(VotingPoll, id=pk)
    method=int(method)
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).annotate(
        vote=Count('voter'))

    len_voters = len(list(set(voters)))

    url_poll = str(reverse_lazy(result_scores, args=(poll.id, method)))
    
    if method ==1:

        title = _('scoring method title')
        label = _('scoring label')
        options = [{'value': 'borda', 'name': _('Borda') if poll.preference_model== "Ranks#0" else _('Range Voting') }, {'value': 'plurality', 'name': _('Plurality')},
                     {'value': 'veto', 'name': _('Veto')},
                     {'value': 'approval', 'name': _('Approval')}, {'value': 'curvea', 'name': _('Curve Approval')}]
        if poll.preference_model== "Approval":
            explanation = mark_safe(_('Approval scoring method explanation'))
        else:
            explanation =  mark_safe(_('scoring method explanation')) if poll.preference_model== "Ranks#0" else mark_safe(_('scoring method explanation without Ranks#0'))

    if method == 2:
        title = _('condorcet method title')
        label = _('condorcet label')
        options = [{'value': 'copeland', 'name': _('Copeland')},
                     {'value': 'simpson', 'name': _('Simpson')}]
        explanation = mark_safe(_('condorcet method explanation'))
        url_poll = "{url}?aggregate=majority".format(
            url = reverse_lazy(view_poll, args=(poll.id, )))

    if method == 3:
        title = _('runoff method title')
        label = _('runoff label')
        options = [{'value': 'trm', 'name': _('Two Round majority')},{'value': 'stv', 'name': _('STV')}]
        explanation = mark_safe(_('runoff method explanation'))

    if method ==4:
        title = _('randomized method title')
        label = _('randomized label')
        options = [
            {'value': 'Shuffle candidates for the first round', 'name': _('Shuffle candidates for the first round')}]
        explanation =mark_safe( _('randomized method explanation'))

    return render(request, 'polls/detail_result.html', locals())


@with_valid_poll
def result_scores(request, poll, method):
    candidates = DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'\
                 else Candidate.objects.filter(poll_id=poll.id)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id)\
                               .values('voter__id','candidate__id','value')\
                               .order_by('last_modification', 'candidate')
    voters = VotingScore.objects.values_list('voter__id', flat=True)\
                                .filter(candidate__poll__id=poll.id)\
                                .order_by('last_modification', 'candidate')
    list_voters =list(set(voters))

    scores = {}

    for v in list_voters:
        scores[str(v)] = {}

    for v in votes:
        scores[str(v["voter__id"])] [str(v["candidate__id"])] = v["value"]

    data= dict()
    method = int(method)
    if method == 1:
        preference_model = preference_model_from_text(poll.preference_model, len(candidates))
        data["scoring"]=scoring_method(candidates,preference_model,votes,list_voters,scores)
    if method == 2:
        data["condorcet"] = condorcet_method(list_voters,candidates,scores)
    if method == 3:
        data["runoff"] = runoff_method(candidates,list_voters,scores)
    if method == 4:
       data["randomized"] = randomized_method(candidates,scores,list_voters)

    return HttpResponse(json.dumps(data, indent=4, sort_keys=True), content_type="application/json")


@with_valid_poll
def data_page(request, poll):
    return render(request, 'polls/data.html', locals())



