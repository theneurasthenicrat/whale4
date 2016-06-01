# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms import  inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.db.models import Count
import json, simplejson
from django.http import HttpResponse, JsonResponse

from accounts.models import WhaleUser
from polls.forms import VotingPollForm, CandidateForm, BaseCandidateFormSet, VotingForm, DateCandidateForm, DateForm, OptionForm
from polls.models import VotingPoll, Candidate, preference_model_from_text, VotingScore, UNDEFINED_VALUE, \
    DateCandidate


# decorators #################################################################


def with_admin_rights(fn):
    def wrapped(request, pk):
        poll = get_object_or_404(VotingPoll, id=pk)
        if request.user is None or request.user != poll.admin:
            messages.error(request, _('you are not admin\'s poll'))
            return redirect(reverse_lazy(home))
        return fn(request,pk)
    return wrapped


def with_voter_rights(fn):
    def wrapped(request, pk,voter):
        poll = get_object_or_404(VotingPoll, id=pk)
        user = get_object_or_404(WhaleUser, id=voter)
        if request.user is not None and request.user.id == user.id:
            return fn(request, pk, voter)
        elif "user_id" in request.session:
            user_id=request.session["user_id"]
            if user_id==user.id:
                return fn(request, pk, voter)
            else:
                messages.error(request, _('This is not your vote'))
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
        else:
            messages.error(request, _('This is not your vote'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
    return wrapped


def yet_vote(fn):
    def wrapped(request, pk):
        poll = get_object_or_404(VotingPoll, id=pk)
        if request.user.is_authenticated():
            votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=request.user.id)
            if votes:
                messages.error(request, _('you have already vote , now you can update your vote'))
                return redirect(reverse_lazy(update_vote, kwargs={'pk': poll.id, 'voter':request.user.id}))
            else:
                return fn(request, pk)
        else:
            return fn(request, pk)
    return wrapped

# simple functions ######################################################################


def days_month(candidates):
    months = []
    days = []
    for c in candidates:

        current_month = c.date.strftime("%B/%Y")
        current_day = c.date.strftime("%A/%d")
        if len(months) > 0 and months[-1]["label"] == current_month:
            months[-1]["value"] += 1
        else:
            months += [{"label": current_month, "value": 1}]
        if len(days) > 0 and months[-1]["label"] == current_month and days[-1]["label"] == current_day:
            days[-1]["value"] += 1
        else:
            days += [{"label": current_day, "value": 1}]
    return days, months


# views ######################################################################


def home(request):
    return render(request, 'polls/home.html', {})


@login_required
def choice(request):
    return render(request, 'polls/choice_ballot.html', {})


@login_required
@with_admin_rights
def success(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/success.html', {'poll': poll})


class VotingPollMixin(object):
    model = VotingPoll
    form_class = VotingPollForm
    template_name = "polls/voting_poll.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VotingPollMixin, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(manage_candidate, kwargs={'pk': self.object.pk,})

    def form_valid(self, form):
        poll = form.save(commit=False)
        poll.save()
        return super(VotingPollMixin, self).form_valid(form)


class VotingPollUpdate(VotingPollMixin, UpdateView):

    @method_decorator(login_required,with_admin_rights)
    def dispatch(self, *args, **kwargs):
        return super(VotingPollMixin, self).dispatch(*args, **kwargs)


class VotingPollCreate(VotingPollMixin, CreateView):

    def form_valid(self, form):
        poll = form.save(commit=False)
        poll.admin = self.request.user
        choice = int(self.kwargs['choice'])
        if choice == 21:
            poll.poll_type = 'Date'
        if choice == 22:
            poll.option_ballots = True
        poll.save()
        return super(VotingPollCreate, self).form_valid(form)


@login_required
@with_admin_rights
def voting_poll_delete(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    admin=request.user.id
    poll.delete()
    messages.success(request, _('Your poll has been deleted!'))
    return redirect(reverse_lazy( 'accountPoll', kwargs={'pk': admin}))


@login_required
@with_admin_rights
def manage_candidate(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    if poll.poll_type != 'Date':
        return redirect(reverse_lazy(candidate_create, kwargs={'pk': poll.id}))
    else:
        return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.id}))


@login_required
@with_admin_rights
def candidate_create(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidateformset = inlineformset_factory(VotingPoll, Candidate,
                                             form=CandidateForm, formset=BaseCandidateFormSet, min_num=2, extra=0,can_delete=False,
                                              validate_min=True)
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()
    candidates_initial = VotingScore.objects.values_list('candidate', flat=True).filter(candidate__poll__id=poll.id).distinct()
    if request.method == 'POST':
        formset = candidateformset(request.POST, instance=poll,prefix='form')

        if formset.is_valid():
            formset.save()
            if voters:
                candidates_final=Candidate.objects.values_list('id', flat=True).filter(poll_id=poll.id)
                candidates_diff=[c for c in candidates_final if c not in candidates_initial]
                for c in candidates_diff:
                    c= get_object_or_404(Candidate, id=c)
                    for voter in voters:
                        voter = get_object_or_404(WhaleUser, id=voter)
                        VotingScore.objects.create(candidate=c, voter=voter, value=UNDEFINED_VALUE)
            messages.success(request, _('Candidates successfully added!'))
            return redirect(reverse_lazy(option, kwargs={'pk': poll.id}))
    else:
        formset = candidateformset(instance=poll,prefix='form')
    return render(request, 'polls/candidate.html', {'formset': formset, 'poll': poll})


@login_required
@with_admin_rights
def date_candidate_create(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    date_candidateformset = inlineformset_factory(VotingPoll, DateCandidate,
                                                  form=DateCandidateForm, formset=BaseCandidateFormSet, extra=1,
                                             can_delete=False)

    candidates = DateCandidate.objects.filter(poll_id=poll.id)
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()
    candidates_initial = VotingScore.objects.values_list('candidate', flat=True).filter(
        candidate__poll__id=poll.id).distinct()
    if request.method == 'POST':
        form = DateForm(request.POST)
        formset = date_candidateformset(request.POST, instance=poll,prefix='form')
        if form.is_valid() and formset.is_valid():
            dates = form.cleaned_data['dates']
            label = formset.save(commit=False)
            for date in dates:
                if label:
                    for candidate in label:
                        cand = DateCandidate()
                        cand.poll = poll
                        cand.date = date
                        cand.candidate=candidate.candidate
                        for c in candidates:
                            if str(c.date) == str(date) and c.candidate == cand.candidate:
                                messages.error(request, _('candidates must be distinct'))
                                return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))
                        cand.save()
                else:
                    cand = DateCandidate()
                    cand.poll = poll
                    cand.date = date
                    for c in candidates:
                        if str(c.date) == str(date)and c.candidate == cand.candidate:
                            messages.error(request, _('candidates must be distinct'))
                            return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))
                    cand.save()
            if voters:
                candidates_final = DateCandidate.objects.values_list('id', flat=True).filter(poll_id=poll.id)
                candidates_diff = [c for c in candidates_final if c not in candidates_initial]
                for c in candidates_diff:
                    c = get_object_or_404(DateCandidate, id=c)
                    for voter in voters:
                        voter = get_object_or_404(WhaleUser, id=voter)
                        VotingScore.objects.create(candidate=c, voter=voter, value=UNDEFINED_VALUE)
            messages.success(request, _('Candidates successfully added!'))
            return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))
    else:
        formset = date_candidateformset(prefix='form')
        form = DateForm()
    return render(request, 'polls/date_candidate.html',
                  {'formset': formset,'form':form, 'poll': poll, 'candidates':candidates})


@login_required
def delete_candidate(request, pk, cand):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidate = get_object_or_404(DateCandidate, id=cand)
    candidate.delete()
    return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.id}))


@login_required
@with_admin_rights
def admin_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.pk,}))


@login_required
@with_admin_rights
def option(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    initial={'option_choice':poll.option_choice,
             'option_modify':poll.option_modify}
    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            poll.option_choice = form.cleaned_data['option_choice']
            poll.option_modify = form.cleaned_data['option_modify']
            poll.save()
            messages.success(request, _('Options successfully added!'))
            return redirect(reverse_lazy(success, kwargs={'pk': poll.id}))
    else:
        form = OptionForm(initial=initial)
        candidates = (
            DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
                poll_id=poll.id))
        if candidates.count() < 2:
            messages.error(request, _('You must add at least two candidates'))
            return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.id,}))
        else:
            return render(request, 'polls/option.html', {'form': form, 'poll': poll})


@yet_vote
def vote(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = (
        DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))
    preference_model = preference_model_from_text(poll.preference_model)
    months = []
    days = []
    if request.user.is_authenticated():
        initial = {'nickname': request.user.nickname}
        voter=request.user
        read=True

    else:
        initial = {}
        read=False
        users = WhaleUser.objects.count() + 1
        email = 'whale4' + str(users) + '@gmail.com'
        voter = WhaleUser.objects.create_user(
        email=email,
        nickname='',
        password='whale4')

    request.session["user_id"] = voter.id

    if poll.poll_type == 'Date':
        (days, months) = days_month(candidates)

    if request.method == 'POST':
        form = VotingForm(candidates, preference_model,poll,read,request.POST)

        if form.is_valid():
            data = form.cleaned_data
            voter.nickname = data['nickname']
            voter.save()
            for c in candidates:
                VotingScore.objects.create(candidate=c, voter=voter, value=data['value' + str(c.id)])
            messages.success(request, _('Your vote has been added to the poll, thank you!'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))
    else:

        form = VotingForm(candidates, preference_model,poll,read,initial=initial)
        cand = []
        for c in candidates:
            if c.candidate:
                cand.append(c.candidate)

    return render(request, 'polls/vote.html', {'form': form, 'poll': poll,'candidates': candidates, 'cand':cand, 'months': months, 'days': days})


@with_voter_rights
def update_vote(request, pk, voter):
    poll = VotingPoll.objects.get(id=pk)
    candidates = (
        DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))
    preference_model = preference_model_from_text(poll.preference_model)
    voter = WhaleUser.objects.get(id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    months = []
    days = []
    initial = {}
    initial['nickname'] = voter.nickname
    for v in votes:
        initial['value' + str(v.candidate.id)] = v.value

    if request.user.is_authenticated():
        read = True
    else:
        read = False

    if poll.poll_type == 'Date':
        (days, months) = days_month(candidates)

    if request.method == 'POST':
        form = VotingForm(candidates, preference_model,poll,read, request.POST)

        if form.is_valid():
            data = form.cleaned_data
            voter.nickname = data['nickname']
            voter.save()
            for v in votes:
                v.value = data['value' + str(v.candidate.id)]
                v.save()
            messages.success(request, _('Your vote has been updated, thank you!'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))
    else:
        form = VotingForm(candidates, preference_model,poll,read, initial=initial)
        cand = []
        for c in candidates:
            if c.candidate:
                cand.append(c.candidate)

    return render(request, 'polls/vote.html',
                  {'form': form, 'poll': poll, 'candidates': candidates, 'cand': cand, 'months': months, 'days': days})



@with_voter_rights
def delete_vote(request, pk, voter):
    poll = get_object_or_404(VotingPoll, id=pk)
    voter = get_object_or_404(WhaleUser, id=voter)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id).filter(voter=voter.id)
    votes.delete()
    messages.success(request, _('Your vote has been deleted!'))
    return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.pk}))


def view_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = (
        DateCandidate.objects.filter(poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
            poll_id=poll.id))
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model)
    months = []
    days = []
    if poll.poll_type == 'Date':
        (days, months) = days_month(candidates)
    scores = {}
    for v in votes:
        if v.voter.id not in scores:
            scores[v.voter.id] = {}
        scores[v.voter.id][v.candidate.id] = v.value

    tab = {}
    for v in votes:
        id = v.voter.id
        tab[id] = {}
        tab[id]['id'] = id
        tab[id]['nickname'] = v.voter.nickname
        tab[id]['scores'] = []
        for c in candidates:
            if c.id in scores[id]:
                score = scores[id][c.id]
                tab[id]['scores'].append({
                    'value': score,
                    'class': 'poll-{0:d}percent'.format(int(round(preference_model.evaluate(score),
                                                                  1) * 100)) if score != UNDEFINED_VALUE else 'poll-undefined',
                    'text': preference_model.value2text(score) if score != UNDEFINED_VALUE else "?"
                })

    values = None if tab == {} else tab.values()
    cand = []
    for c in candidates:
        if c.candidate:
            cand.append(c.candidate)
    return render(request, 'polls/poll.html',
                  {'poll': poll, 'candidates': candidates, 'votes': values, 'cand':cand,'months': months, 'days': days})


def view_poll_json(request,pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model)
    scores = [ ]
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()
    for voter in voters:
        user = get_object_or_404(WhaleUser, id=voter)
        values = VotingScore.objects.values_list('value', flat=True).filter(candidate__poll__id=poll.id).filter(
            voter=voter)
        v = {}
        v['name'] =user.nickname
        v['values']=[value for value in values]
        scores.append(v)

    candidates = (
        DateCandidate.objects.values_list('candidate','date').filter(poll_id=poll.id) if poll.poll_type == 'Date'else
        Candidate.objects.values_list('candidate', flat=True).filter(poll_id=poll.id))

    cand= [y.strftime("%d/%m/%Y")+'#'+c for c,y in candidates] if poll.poll_type == 'Date' else [c for c in candidates]

    json_object = {}
    json_object['preferenceModel']= preference_model.as_dict()
    json_object['type'] = 1 if poll.poll_type == 'Date' else 0
    json_object['candidates'] = cand
    json_object['votes'] = scores

    return HttpResponse(simplejson.dumps(json_object,indent=4, sort_keys=True),content_type="application/json")


class WhaleUserDetail(DetailView):

    model = WhaleUser
    template_name = "polls/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(WhaleUserDetail, self).get_context_data(**kwargs)
        context['poll_list'] = VotingPoll.objects.filter(admin_id= self.kwargs['pk'])
        context['poll_list_voter'] = VotingPoll.objects.filter(candidates__votingscore__voter_id=self.kwargs['pk']).annotate(total=Count('id'))
        return context

    @method_decorator(login_required, with_admin_rights)
    def dispatch(self, *args, **kwargs):
        return super(WhaleUserDetail, self).dispatch(*args, **kwargs)


def bad_request(request):
    response = render_to_response('polls/400.html', {}, context_instance=RequestContext(request))
    response.status_code = 400
    return response


def permission_denied(request):
    response = render_to_response('polls/403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response


def page_not_found(request):
    response = render_to_response('polls/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def server_error(request):
    response = render_to_response('polls/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
