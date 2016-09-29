# -*- coding: utf-8 -*-

import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.utils.safestring import mark_safe
from operator import itemgetter
from datetime import datetime,date
from random import  shuffle

from django.db.models import Count

from accounts.models import WhaleUser, WhaleUserAnonymous, User, UserAnonymous
from polls.forms import VotingPollForm, CandidateForm,  VotingForm,  DateForm, \
    OptionForm, InviteForm, BallotForm, NickNameForm, StatusForm, PollUpdateForm
from polls.models import VotingPoll, Candidate, preference_model_from_text, VotingScore, UNDEFINED_VALUE, \
    DateCandidate

from polls.utils import days_months, voters_undefined, scoring_method,\
    condorcet_method, runoff_method, randomized_method


# decorators #################################################################


def with_admin_rights(fn):
    def wrapped(request, pk,*args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if request.user is None or request.user != poll.admin:
            messages.error(request, mark_safe(_("you are not the poll administrator")))
            return redirect(reverse_lazy('redirectPage'))
        return fn(request,pk,*args, **kwargs)
    return wrapped


def with_voter_rights(fn):
    def wrapped(request, pk,voter):
        poll = get_object_or_404(VotingPoll, id=pk)
        user = get_object_or_404(User, id=voter)
        if poll.ballot_type =="Experimental":
            messages.error(request, mark_safe(_('Experimental vote can not be updated')))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
        if poll.ballot_type =="Secret" :
            if "user" in request.session and request.session["user"]==user.id:
                return fn(request, pk, voter)
            else:
                messages.error(request, mark_safe(_('This is not your vote')))
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))

        if not (isinstance(user,WhaleUser)) or (request.user is not None and request.user.id == user.id):
            return fn(request, pk, voter)
        else:
            messages.error(request, mark_safe(_('This is not your vote')))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))

    return wrapped


def with_view_rights(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.ballot_type=="Experimental" and (request.user is None or request.user != poll.admin):
            messages.error(request,  mark_safe(_("you are not the poll administrator")))
            return redirect(reverse_lazy('redirectPage'))
        elif poll.ballot_type=="Secret" and poll.closing_poll():
            messages.error(request, mark_safe(_("The poll is not closed")))
            return redirect(reverse_lazy('redirectPage'))
        return fn(request, pk, *args, **kwargs)

    return wrapped


def certificate_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        path = request.get_full_path()
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.ballot_type=="Secret" and "user" not in request.session:
            return redirect('/polls/certificate/'+str(poll.id)+ '?next=' +str(path))
        return fn(request, pk, *args, **kwargs)
    return wrapped


def status_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.ballot_type=="Experimental" and (not poll.status_poll):
            return redirect(reverse_lazy('redirectPage'))
        return fn(request, pk, *args, **kwargs)
    return wrapped


def minimum_candidates_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        candidates =  Candidate.objects.filter(poll_id=poll.id)
        if candidates.count() < 2:
            messages.error(request, mark_safe(_('You must add at least two candidates')))
            return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.id,}))
        return fn(request, pk, *args, **kwargs)
    return wrapped


# views ######################################################################


def bad_request(request):
    return render(request,'polls/error.html',status=400)


def permission_denied(request):
    return render(request,'polls/error.html',status=403)


def page_not_found(request):
    return render(request,'polls/error.html',status=404)


def server_error(request):
    return render(request,'polls/error.html',status=500)


def home(request):
    return render(request, 'polls/home.html')


def redirect_page(request):
    return render(request, 'polls/redirectPage.html')


@login_required
def choice(request):
    request.session["update"] = 0
    return render(request, 'polls/new_poll.html')


@login_required
@with_admin_rights
@minimum_candidates_required
def admin_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    request.session["update"] = 1
    return render(request, 'polls/admin.html',locals())


@login_required
def new_poll(request, choice ):

    form = VotingPollForm()

    if "update" in request.session:
        update_poll = False if int(request.session["update"]) == 1 else True

    if request.method == 'POST':
        form =  VotingPollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.admin = request.user
            if int(choice) == 21:
                poll.poll_type = 'Date'
            if int(choice) == 22:
                poll.ballot_type = 'Secret'
            if int(choice) ==23:
                poll.ballot_type = 'Experimental'

            poll.save()
            messages.success(request, mark_safe(_('General parameters successfully created!')))
            return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.pk}))
    return render(request, 'polls/parameters_poll.html', locals())


@login_required
@with_admin_rights
def update_voting_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    update_poll=True
    if "update" in request.session:
        update_poll = False if int(request.session["update"]) == 1 else True

    form = VotingPollForm(instance=poll) if update_poll else PollUpdateForm(instance=poll)

    if request.method == 'POST':
        form = VotingPollForm(request.POST, instance=poll)if update_poll else PollUpdateForm(request.POST,instance=poll)
        if form.is_valid():
            poll = form.save(commit=False)
            if "update" in request.session and int(request.session["update"]) == 1:
                close_now_option = form.cleaned_data['close_now']
                if close_now_option:
                    poll.closing_date= date.today()
            poll.save()
            if update_poll:
                messages.success(request, mark_safe(_('General parameters successfully updated!')))
                return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.pk}))
            else:
                messages.success(request, mark_safe(_('Parameters are successfully updated!')))
                return redirect(reverse_lazy(admin_poll, kwargs={'pk': poll.pk}))
    return render(request, 'polls/parameters_poll.html', locals())


@login_required
@with_admin_rights
def delete_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    admin=request.user.id
    poll.delete()
    messages.success(request, mark_safe(_('Your poll has been deleted!')))
    return redirect(reverse_lazy( 'accountPoll', kwargs={'pk': admin}))


@login_required
@with_admin_rights
@minimum_candidates_required
def option(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    form = OptionForm(instance=poll)
    if request.method == 'POST':
        form = OptionForm(request.POST, instance=poll)
        if form.is_valid():
            poll = form.save()
            messages.success(request,  mark_safe(_('Options are successfully added!')))
            return redirect(reverse_lazy(success, kwargs={'pk': poll.id}))
    return render(request, 'polls/option.html', locals())


@login_required
@with_view_rights
def status(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    form = StatusForm(instance=poll)
    if request.method == 'POST':
        form = StatusForm(request.POST,instance=poll)
        if form.is_valid():
            poll = form.save()
            messages.success(request, mark_safe(_('Status is successfully changed!')))
            return redirect(reverse_lazy(admin_poll, kwargs={'pk': poll.id}))
    return render(request, 'polls/status_poll.html',locals())


@login_required
@with_admin_rights
def manage_candidate(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    if poll.option_modify:
        if poll.poll_type != 'Date':
            return redirect(reverse_lazy(candidate_create, kwargs={'pk': poll.id}))
        else:
            return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.id}))
    else:
        messages.error(request, mark_safe(_('Add or remove candidates is not allowed!')))
        return redirect(reverse_lazy('redirectPage'))


@login_required
@with_admin_rights
def candidate_create(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = Candidate.objects.filter(poll_id=poll.id)
    form = CandidateForm()

    if "update" in request.session:
        update_poll = False if int(request.session["update"]) == 1 else True

    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.poll = poll
            equal_candidate=[c for c in candidates if str(c) == str(candidate)]
            if equal_candidate:
                messages.error(request, mark_safe(_('Candidates must be distinct (%(c)s)') % {'c': candidate.candidate}))
            else:
                candidate.save()
                voters_undefined(poll)
                messages.success(request, mark_safe(_('Candidate %(c)s successfully added!') % {'c': candidate.candidate}))
        return redirect(reverse_lazy(candidate_create, kwargs={'pk': poll.pk}))
    return render(request, 'polls/candidate.html', locals())


@login_required
@with_admin_rights
def date_candidate_create(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = DateCandidate.objects.filter(poll_id=poll.id)
    form = DateForm()

    if "update" in request.session:
        update_poll = False if int(request.session["update"]) == 1 else True
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid() :
            dates = form.cleaned_data['dates']
            label = form.cleaned_data['candidate']
            for date in dates:
                candidate = DateCandidate()
                candidate.poll = poll
                candidate.date = date
                candidate.candidate=label
                for c in candidates:
                    if str(c.date) == str(date)and c.candidate == candidate.candidate:
                        messages.error(request,  mark_safe(_('Candidates must be distinct (%(c)s)') % {'c': candidate.candidate}))
                        return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))
                candidate.save()

            voters_undefined(poll)
            messages.success(request,  mark_safe(_('Candidates are successfully added!')))
            return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))

    return render(request, 'polls/date_candidate.html',locals())


@login_required
@with_admin_rights
def delete_candidate(request, pk, cand):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidate = get_object_or_404(Candidate, id=cand)
    candidate.delete()
    messages.success(request,  mark_safe(_('Candidate has been deleted (%(c)s)!') % {'c': candidate.candidate}))
    return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.id}))


@login_required
@with_admin_rights
def success(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    if "update" in request.session:
        update_poll = False if int(request.session["update"]) == 1 else True
    if poll.ballot_type=="Secret":
        inviters = WhaleUserAnonymous.objects.filter(poll=poll.id)
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            emails =form.cleaned_data['email']

            for email in emails:
                certi = WhaleUserAnonymous.id_generator()
                inviter = WhaleUserAnonymous.objects.create(
                    nickname=WhaleUserAnonymous.nickname_generator(poll.id) , email=email,
                    certificate=WhaleUserAnonymous.encodeAES(certi),poll=poll
                )
                subject, from_email, to = 'Invite to the secret poll', 'whale4.ad@gmail.com', email
                htmly = get_template('polls/email.html')
                url="http://strokes.imag.fr/whale4/polls/vote/"+str(poll.pk)
                d = Context({'poll': poll, 'certi':certi,'url':url})
                html_content = htmly.render(d)
                msg = EmailMessage(subject, html_content, from_email, [to])
                msg.content_subtype = "html"
                msg.send()

            messages.success(request, mark_safe(_('Invited voters successfully added!')))
            return redirect(reverse_lazy(success, kwargs={'pk': poll.id}))
    else:
        form = InviteForm()
    return render(request, 'polls/invite.html', locals())


@login_required
@with_admin_rights
def delete_anonymous(request,pk,voter):
    poll = get_object_or_404(VotingPoll, id=pk)
    voter = get_object_or_404(WhaleUserAnonymous, id=voter)
    if "user" in request.session:
        del request.session["user"]
    voter.delete()
    messages.success(request,  mark_safe(_('anonymous voter has been deleted!')))
    return redirect(reverse_lazy(success, kwargs={'pk': poll.pk}))


def certificate(request, pk):
    next_url = None
    if request.GET:
        next_url = request.GET['next']

    poll = get_object_or_404(VotingPoll, id=pk)
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
                return redirect(reverse_lazy('certificate', kwargs={'pk': poll.id}))

    return render(request, 'polls/certificate.html', locals())


@certificate_required
@status_required
def vote(request, pk):

    poll = get_object_or_404(VotingPoll, id=pk)
    candidates =Candidate.objects.filter(poll_id=poll.id)
    if poll.option_shuffle:
        candidates=list(candidates)
        shuffle(candidates)

    preference_model = preference_model_from_text(poll.preference_model, len(candidates))
    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)

    read = True
    if not poll.ballot_type=="Secret":
        if poll.ballot_type=="Experimental":
            voter = UserAnonymous(nickname=UserAnonymous.nickname_generator(poll.id), poll=poll)
        elif request.user.is_authenticated():
            voter=request.user
        else:
            read=False
            voter = User()
    else:
        user_id = request.session["user"]
        voter = get_object_or_404(WhaleUserAnonymous, id= user_id)

    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    if votes:
        messages.info(request,  mark_safe(_('you have already voted, now you can update your vote')))
        return redirect(reverse_lazy(update_vote, kwargs={'pk': poll.id, 'voter': voter.id}))

    form = VotingForm(candidates, preference_model,poll)

    form1= NickNameForm(read,initial={'nickname':voter.nickname})
    cand = [c.candidate for c in candidates if c.candidate]
    if request.method == 'POST':
        if poll.ballot_type=="Secret" and "user" in request.session:
            del request.session["user"]
        form = VotingForm(candidates, preference_model,poll,request.POST)
        form1 = NickNameForm(read, request.POST)

        if form.is_valid() and form1.is_valid():
            voter.nickname = form1.cleaned_data['nickname']
            voter.save()
            today = datetime.now()
            for c in candidates:
                VotingScore.objects.create(candidate=c,last_modification=today, voter=voter, value=form.cleaned_data['value' + str(c.id)])
            messages.success(request,  mark_safe(_('Your vote has been added to the poll, thank you!')))
            if poll.ballot_type=="Secret":
                return redirect(reverse_lazy(view_poll_secret, kwargs={'pk': poll.pk,'voter':voter.id}))
            elif poll.ballot_type=="Experimental":
                poll.status_poll=False
                poll.save()
                messages.info(request, mark_safe(_('Thank you for voting')))
                return redirect(reverse_lazy('redirectPage'))
            else:
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))

    return render(request, 'polls/vote.html', locals())


@certificate_required
@with_voter_rights
def update_vote(request, pk, voter):
    poll = VotingPoll.objects.get(id=pk)
    candidates =Candidate.objects.filter(poll_id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))
    voter = User.objects.get(id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)

    initial = dict()
    for v in votes:
        initial['value' + str(v.candidate.id)] = v.value
    read = True
    if not poll.ballot_type=="Secret" and not request.user.is_authenticated():
        read = False

    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)


    form = VotingForm(candidates, preference_model,poll, initial=initial)
    form1 = NickNameForm(read,initial={'nickname':voter.nickname})
    cand = [c.candidate for c in candidates if c.candidate]
    if request.method == 'POST':
        form = VotingForm(candidates, preference_model,poll, request.POST)
        form1 = NickNameForm(read, request.POST)
        if poll.ballot_type=="Secret" and "user" in request.session:
            del request.session["user"]
        if form.is_valid() and form1.is_valid():
            data = form.cleaned_data
            voter.nickname = form1.cleaned_data['nickname']
            voter.save()
            today=datetime.now()
            for v in votes:
                v.value = data['value' + str(v.candidate.id)]
                v.last_modification= today
                v.save()
            messages.success(request,  mark_safe(_('Your vote has been updated, thank you!')))
            if poll.ballot_type=="Secret":
                return redirect(reverse_lazy(view_poll_secret, kwargs={'pk': poll.pk, 'voter': voter.id}))
            else:
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))

    return render(request, 'polls/vote.html',locals())


@certificate_required
@with_voter_rights
def delete_vote(request, pk, voter):

    poll = get_object_or_404(VotingPoll, id=pk)
    voter = get_object_or_404(User, id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    votes.delete()
    if poll.ballot_type=="Secret":
        del request.session["user"]
    messages.success(request,  mark_safe(_('Your vote has been deleted!')))
    if poll.ballot_type=="Secret":
        return redirect(reverse_lazy(view_poll_secret, kwargs={'pk': poll.pk, 'voter': voter.id}))
    else:
        return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))


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


@with_view_rights
def view_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)

    if "format" in request.GET:
        if request.GET['format'] == 'json':
            return _view_poll_as_json(poll)
        if request.GET['format'] == 'csv':
            return _view_poll_as_csv(poll)
        if request.GET['format'] == 'preflib':
            return _view_poll_as_preflib(poll)

    closing_poll = poll.closing_poll()
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
        'closing_poll':closing_poll
    })

def _view_poll_as_json(poll):
    return HttpResponse(json.dumps(dict(poll), indent=4, sort_keys=True),
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


def result_all(request, pk ):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/all_result.html', locals())


def result_view(request, pk ,method):
    poll = get_object_or_404(VotingPoll, id=pk)
    method=int(method)
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).annotate(
        vote=Count('voter'))

    len_voters = len(list(set(voters)))

    if method ==1:

        title = _('scoring method title')
        label = _('scoring label')
        options = [{'value': 'borda', 'name': _('Borda') if poll.preference_model== "Ranks#0" else _('Semi-Borda') }, {'value': 'plurality', 'name': _('Plurality')},
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

    if method == 3:
        title = _('runoff method title')
        label = _('runoff label')
        options = [{'value': 'stv', 'name': _('STV')}, {'value': 'trm', 'name': _('Two Round majority')}]
        explanation = mark_safe(_('runoff method explanation'))

    if method ==4:
        title = _('randomized method title')
        label = _('randomized label')
        options = [
            {'value': 'Shuffle candidates for the first round', 'name': _('Shuffle candidates for the first round')}]
        explanation =mark_safe( _('randomized method explanation'))

    return render(request, 'polls/detail_result.html', locals())


def result_scores(request, pk,method):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = Candidate.objects.filter(poll_id=poll.id)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).values('voter__id','candidate__id','value')
    voters = VotingScore.objects.values_list('voter__id', flat=True).filter(candidate__poll__id=poll.id)
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
        data["scoring"]=scoring_method(candidates,preference_model,votes)
    if method == 2:
        data["condorcet"] = condorcet_method(list_voters,candidates,scores)
    if method == 3:
        data["runoff"] = runoff_method(candidates,list_voters,scores)
    if method == 4:
       data["randomized"] = randomized_method(candidates,scores,list_voters)

    return HttpResponse(json.dumps(data, indent=4, sort_keys=True), content_type="application/json")


def data_page(request, pk ):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/data.html', locals())



