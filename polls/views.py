# -*- coding: utf-8 -*-
from operator import itemgetter
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
from random import sample, shuffle
from math import log2, modf,pow

from accounts.models import WhaleUser, WhaleUserAnonymous, User, UserAnonymous
from polls.forms import VotingPollForm, CandidateForm,  VotingForm,  DateForm, \
    OptionForm, InviteForm, BallotForm, NickNameForm, StatusForm, PollUpdateForm
from polls.models import VotingPoll, Candidate, preference_model_from_text, VotingScore, UNDEFINED_VALUE, \
    DateCandidate

from polls.utils import days_months, voters_undefined


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
        if poll.option_experimental:
            messages.error(request, mark_safe(_('Experimental vote can not be updated')))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
        if poll.option_ballots :
            if "user" in request.session and request.session["user"]==user.id:
                return fn(request, pk, voter)
            else:
                messages.error(request, mark_safe(_('This is not your vote')))
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))

        if request.user is not None and request.user.id == user.id:
            return fn(request, pk, voter)
        else:
            messages.error(request, mark_safe(_('This is not your vote')))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))

    return wrapped


def with_view_rights(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.option_experimental and (request.user is None or request.user != poll.admin):
            messages.error(request,  mark_safe(_("you are not the poll administrator")))
            return redirect(reverse_lazy('redirectPage'))
        elif poll.option_ballots and poll.closing_poll():
            messages.error(request, mark_safe(_("The poll is not closed")))
            return redirect(reverse_lazy('redirectPage'))
        return fn(request, pk, *args, **kwargs)

    return wrapped


def certificate_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        path = request.get_full_path()
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.option_ballots and "user" not in request.session:
            return redirect('/polls/certificate/'+str(poll.id)+ '?next=' +str(path))
        return fn(request, pk, *args, **kwargs)
    return wrapped


def status_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.option_experimental and (not poll.status):
            return redirect(reverse_lazy('redirectPage'))
        return fn(request, pk, *args, **kwargs)
    return wrapped


def minimum_candidates_required(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
                poll_id=poll.id))
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
        form = VotingPollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.admin = request.user
            if int(choice) == 21:
                poll.poll_type = 'Date'
            if int(choice) == 22:
                poll.option_ballots = True
            if int(choice) ==23:
              poll.option_experimental = True

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
            if poll.option_close_poll:
                poll.closing_date= date.today()
            poll = form.save()
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
    print(form)
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
    if poll.option_ballots:
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
                url="http://localhost:8000"+str(reverse_lazy(vote, kwargs={'pk': poll.pk}))
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
    candidates = ( DateCandidate.objects.filter(poll_id=poll.id) \
                       if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
    if poll.option_shuffle:
        candidates=list(candidates)
        shuffle(candidates)

    preference_model = preference_model_from_text(poll.preference_model, len(candidates))
    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)

    read = True
    if not poll.option_ballots:
        if poll.option_experimental:
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
        if poll.option_ballots and "user" in request.session:
            del request.session["user"]
        form = VotingForm(candidates, preference_model,poll,request.POST)
        form1 = NickNameForm(read, request.POST)
        print(form)
        if form.is_valid() and form1.is_valid():
            voter.nickname = form1.cleaned_data['nickname']
            voter.save()
            for c in candidates:
                VotingScore.objects.create(candidate=c, voter=voter, value=form.cleaned_data['value' + str(c.id)])
            messages.success(request,  mark_safe(_('Your vote has been added to the poll, thank you!')))
            if poll.option_ballots:
                return redirect(reverse_lazy(view_poll_secret, kwargs={'pk': poll.pk,'voter':voter.id}))
            elif poll.option_experimental:
                poll.status=False
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
    candidates = (
        DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))
    voter = User.objects.get(id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)

    initial = dict()
    for v in votes:
        initial['value' + str(v.candidate.id)] = v.value
    read = True
    if not poll.option_ballots and not request.user.is_authenticated():
        read = False

    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)


    form = VotingForm(candidates, preference_model,poll, initial=initial)
    form1 = NickNameForm(read,initial={'nickname':voter.nickname})
    cand = [c.candidate for c in candidates if c.candidate]
    if request.method == 'POST':
        form = VotingForm(candidates, preference_model,poll, request.POST)
        form1 = NickNameForm(read, request.POST)
        if poll.option_ballots and "user" in request.session:
            del request.session["user"]
        if form.is_valid() and form1.is_valid():
            data = form.cleaned_data
            voter.nickname = form1.cleaned_data['nickname']
            voter.save()
            for v in votes:
                v.value = data['value' + str(v.candidate.id)]
                v.last_modification= datetime.now()
                v.save()
            messages.success(request,  mark_safe(_('Your vote has been updated, thank you!')))
            if poll.option_ballots:
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
    if poll.option_ballots:
        del request.session["user"]
    messages.success(request,  mark_safe(_('Your vote has been deleted!')))
    if poll.option_ballots:
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
    closing_poll=poll.closing_poll()
    candidates = (
        DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))
    cand = [ c.candidate for c in candidates if c.candidate]
    voting = VotingScore.objects.filter(candidate__poll__id=poll.id).order_by('last_modification')
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))

    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)

    scores = {}
    for v in voting:
        if v.voter.id not in scores:
            scores[v.voter.id] = {}
        scores[v.voter.id][v.candidate.id] = v.value

    tab = {}
    for v in voting:
        id = v.voter.id
        tab[id] = {}
        tab[id]['id'] = id
        tab[id]['nickname'] = v.voter.nickname
        tab[id]['scores'] = []
        for c in candidates:
            score= scores[v.voter.id][c.id]
            tab[id]['scores'].append(
                {'value': score,
                 'class': 'poll-{0:d}percent'.format(
                     int(round(preference_model.evaluate(score),
                               1) * 100)) if score != UNDEFINED_VALUE else 'poll-undefined',
                 'text': preference_model.value2text(score)

                 })

    votes= tab.values()

    list1 = list()
    scores=[]
    voters=[]
    if votes:
        for value in votes:
            v = dict()
            v['name'] = value['nickname']
            score= [val['value'] for val in value['scores']]
            text=[val['text'] for val in value['scores']]
            v['values'] = score
            text.insert(0,value['nickname'])
            voters.append(text)
            list1.append(v)
            scores.append(score)

    if "format" in request.GET and request.GET['format'] == 'json':
        json_object = dict()
        json_object[
            'preferenceModel'] = preference_model.as_dict_option() if poll.option_choice else preference_model.as_dict()
        json_object['type'] = 1 if poll.poll_type == 'Date' else 0
        json_object['candidates'] = [str(c) for c in candidates]
        json_object['votes'] = list1

        return HttpResponse(json.dumps(json_object, indent=4, sort_keys=True), content_type="application/json")

    elif "format" in request.GET and request.GET['format'] == 'preflib':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="poll-preflib.csv"'
        response.write(str(len(candidates)) + '\n')
        dict_candidates=dict()
        for i, c in enumerate(candidates):
            dict_candidates[str(c)]=i+1
            response.write('{n},{l}\n'.format(n=i + 1, l=str(c)))
        len_votes = len(votes) if votes else 0
        response.write('{a},{b},{c}\n'.format(a=len_votes, b=len_votes, c= len_votes))

        for i,score in enumerate(scores):
            values = zip(candidates, score)
            values_sorted = sorted(values, key=itemgetter(1), reverse=True)
            values = map(list, zip(*values_sorted))
            candidate_score=[]
            for k, c in enumerate(values):
                candidate_score.insert(k, c)
            row_voter=[]
            j=0
            while j<len(candidate_score[1]):
                counter=candidate_score[1].count(candidate_score[1][j])
                if counter==1:
                    row_voter.append(dict_candidates[ str(candidate_score[0][j])])
                    j += 1
                else:
                    x=set([dict_candidates[str(c)] for c in candidate_score[0][j:j+counter] ])
                    row_voter.append(x)
                    j += counter
            response.write(','.join([str(x) for x in ([i+1]+row_voter)]))
            response.write('\n')
        return response

    elif"format" in request.GET and request.GET['format'] == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="poll-csv.csv"'
        response.write(','.join(['voter']+[str(c) for c in candidates] ))
        response.write('\n')
        for voter in voters:
            response.write(','.join([str(x) for x in voter]))
            response.write('\n')

        return response

    else:
        return render(request, 'polls/view_poll.html', locals())


def result_all(request, pk ):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/all_result.html', locals())


def result_view(request, pk ,method):
    poll = get_object_or_404(VotingPoll, id=pk)
    method=int(method)
    if method ==1:
        title = _('scoring method title')
        label = _('scoring label')
        options = [{'value': 'borda', 'name': _('Borda')}, {'value': 'plurality', 'name': _('Plurality')},
                     {'value': 'veto', 'name': _('Veto')},
                     {'value': 'approval', 'name': _('Approval')}, {'value': 'curvea', 'name': _('Curve Approval')}]
        explanation =  mark_safe(_('scoring method explanation'))

    if method == 2:
        title = _('condorcet method title')
        label = _('condorcet label')
        options = [{'value': 'Copeland 0', 'name': _('Copeland 0')}, {'value': _('Copeland 1'), 'name': _('Copeland 1')},
                     {'value': 'Simpson', 'name': _('Simpson')}]
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


def result_scores(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = (DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))

    votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model, len(candidates))
    scores = {}
    for c in candidates:
        scores[c.id] = []
    for v in votes:
        scores[v.candidate.id].append(v.value)

    approval = dict()

    approval["threshold"] = preference_model.values[1:]
    candi = []
    borda_scores = []
    plurality_scores = []
    veto_scores = []
    randomized_scores=[]
    nodes=[]
    matrix=[]
    for c in candidates:
        sum_borda = 0
        sum_plurality = 0
        sum_veto = 0
        node={}
        runoff={}
        for score in scores[c.id]:
            sum_borda = sum_borda + (score if score != UNDEFINED_VALUE else 0)
            sum_plurality = sum_plurality + (1 if score == preference_model.max() else 0)
            sum_veto = sum_veto + (1 if score != (preference_model.min()) else 0)
        candi.append(str(c))
        node["name"]=str(c)
        node["value"]=sum_borda
        runoff["name"]=str(c)
        runoff["plurality"]=sum_plurality
        runoff["borda"]=sum_borda
        matrix.append(runoff)
        nodes.append(node)
        borda_scores.append({"x":str(c),"y":sum_borda})
        randomized_scores.append({"name":str(c),"value":sum_borda,"parent":str(c)})
        plurality_scores.append({"x":str(c),"y":sum_plurality})

        veto_scores.append({"x":str(c),"y":sum_veto})
    approval_scores = []
    curve_approval=[]
    for y in approval["threshold"]:
        th = []
        for c in candidates:
            sum_approval = 0
            for score in scores[c.id]:
                sum_approval = sum_approval + (1 if score >= y else 0)
            th.append({"x":str(c),"y":sum_approval})
            curve_approval.append({"candidate":str(c),"x":y,"y":sum_approval})

        approval_scores.append(th)
    if preference_model.id == "rankingNoTies" or preference_model.id == "rankingWithTies":
        approval_scores.reverse()


    i=0
    n= len(candi)
    links=[]
    nodes= sorted(nodes, key=itemgetter('value'),reverse=True)
    while(i<n-1):
        j=i+1
        while(j<n):

            a= nodes[i]["value"]
            b= nodes[j]["value"]
            link = {}
            link["value"]=abs(a-b)
            if a-b >=0 :
                link["source"]=i
                link["target"]=j

            else:
                link["source"] = j
                link["target"] = i
            links.append(link)
            j=j+1
        i=i+1
    matrix= sorted(matrix, key=itemgetter('plurality','borda'),reverse=True)
    n = len(candi)
    matrix1=[]
    while n>0:
        matrix1.append(matrix[:n])
        n=n-1

    list_round=[]

    len_cand=len(candi)
    a,b=modf( log2(len_cand))
    if a!=0:
        n=len_cand-pow(2,b)
    else:
        n=len_cand/2

    while(n>0):
        h=sample(randomized_scores,2)
        parent=h[0] if h[0]["value"] > h[1]["value"] else h[1]
        h[0]["parent"]=parent["name"]
        h[1]["parent"]=parent["name"]
        h[0]["diff"]= h[0]["value"]-h[1]["value"]
        h[1]["diff"]= h[1]["value"]-h[0]["value"]

        list_round.append({"name":parent["name"],"value":parent["value"],"parent":"null","children":h})
        randomized_scores.remove(h[0])
        randomized_scores.remove(h[1])
        n=n-1
    list_x=[{"name":x["name"],"value":x["value"],"parent":"null","children":[x]} for x in randomized_scores]
    list_round.extend(list_x)

    n = len(list_round)

    j=log2(n)
    round =j+1
    list_p=list_round
    while(j>0):
        list_round1=[]
        i = 0
        while(i<n):
            parent=list_p[i] if list_p[i]["value"] > list_p[i + 1]["value"] else list_p[i + 1]
            list_p[i]["parent"]=parent["name"]
            list_p[i]["diff"]=list_p[i]["value"]-list_p[i + 1]["value"]
            list_p[i+1]["parent"]=parent["name"]
            list_p[i+1]["diff"] = list_p[i+1]["value"] - list_p[i]["value"]

            list_round1.append({"name":parent["name"],"parent":"null","value":parent["value"],"children":list_p[i:i+2]})
            i=i+2
        n=len(list_round1)

        list_p=list_round1[:]
        j=j-1



    approval["scores"] = approval_scores

    score_method = dict()
    score_method["borda"] = borda_scores
    score_method["plurality"] = plurality_scores
    score_method["veto"] = veto_scores
    score_method["approval"] = approval
    score_method["curve_approval"] = curve_approval

    condorcet_method = dict()
    condorcet_method["nodes"] = nodes
    condorcet_method["links"] = links

    runoff_method = dict()
    runoff_method["stv"]= matrix1
    runoff_method["trm"]= [matrix,matrix[:2],matrix[:1]]

    randomized_method = {"list":list_p,"round":round}


    method= dict()
    method["scoring"]=score_method
    method["condorcet"] = condorcet_method
    method["runoff"] = runoff_method
    method["randomized"] = randomized_method

    return HttpResponse(json.dumps(method, indent=4, sort_keys=True), content_type="application/json")


def data_page(request, pk ):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/data.html', locals())