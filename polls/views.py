# -*- coding: utf-8 -*-
from operator import itemgetter
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context

from accounts.models import WhaleUser, WhaleUserAnonymous, User, UserAnonymous
from polls.forms import VotingPollForm, CandidateForm, BaseCandidateFormSet, VotingForm, DateCandidateForm, DateForm, \
    OptionForm, VotingPollUpdateForm, InviteForm, BallotForm, NickNameForm, StatusForm
from polls.models import VotingPoll, Candidate, preference_model_from_text, VotingScore, UNDEFINED_VALUE, \
    DateCandidate

from polls.utils import days_months, voters_undefined


# decorators #################################################################


def with_admin_rights(fn):
    def wrapped(request, pk,*args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if request.user is None or request.user != poll.admin:
            messages.error(request, _("you are not admin's poll"))
            return redirect(reverse_lazy(home))
        return fn(request,pk,*args, **kwargs)
    return wrapped


def with_voter_rights(fn):
    def wrapped(request, pk,voter):
        poll = get_object_or_404(VotingPoll, id=pk)
        user = get_object_or_404(User, id=voter)
        if poll.option_experimental:
            messages.error(request, _('Experimental vote can not be updated'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
        elif poll.option_ballots :
            if ("user" in request.session and request.session["user"]==user.id):
                return fn(request, pk, voter)
            else:
                messages.error(request, _('Experimental vote can not be updated'))
                return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))

        elif ( request.user is not None and request.user.id == user.id \
                or not isinstance(user,WhaleUser)):
            return fn(request, pk, voter)
        else:
            messages.error(request, _('This is not your vote'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
    return wrapped


def with_view_rights(fn):
    def wrapped(request, pk, *args, **kwargs):
        poll = get_object_or_404(VotingPoll, id=pk)
        if poll.option_experimental and (request.user is None or request.user != poll.admin):
            messages.error(request, _("you are not admin's poll"))
            return redirect(reverse_lazy(home))
        elif poll.option_ballots and poll.closing_poll():
            messages.error(request, _("The poll is not closed"))
            return redirect(reverse_lazy(home))
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
            return redirect(reverse_lazy(home))
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


def experimental(request):
    return render(request, 'polls/experimental.html')


@login_required
@with_admin_rights
def admin_poll(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    if poll.option_choice or poll.option_modify:
        messages.error(request, _('You are not allowed to update the poll'))
        return redirect(reverse_lazy(home))
    else:
        return redirect(reverse_lazy('updateVotingPoll', kwargs={'pk': poll.pk,}))


@login_required
def choice(request):
    return render(request, 'polls/choice_ballot.html')


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

    form_class = VotingPollUpdateForm

    @method_decorator(with_admin_rights)
    @method_decorator(login_required)
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
        if choice ==23:
          poll.option_experimental = True

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
    candidates = Candidate.objects.filter(poll_id=poll.id)
    candidateformset = inlineformset_factory(VotingPoll, Candidate, form=CandidateForm,
                                             formset=BaseCandidateFormSet, extra=1, can_delete=False)
    formset = candidateformset(prefix='form')
    print(formset)
    if request.method == 'POST':
        formset = candidateformset(request.POST, instance=poll, prefix='form')
        if formset.is_valid():
            labels = formset.save(commit=False)
            equal_label=[c for c in candidates for ca in labels  if str(c)== str(ca)]
            if not equal_label:
                for candidate in labels:
                    candidate.save()
                voters_undefined(poll)
                messages.success(request, _('Candidates successfully added!'))
            else:
                messages.error(request, _('candidates must be distinct'))

        return redirect(reverse_lazy(candidate_create, kwargs={'pk': poll.pk}))

    return render(request, 'polls/candidate.html', locals())


@login_required
@with_admin_rights
def date_candidate_create(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = DateCandidate.objects.filter(poll_id=poll.id)
    date_candidateformset = inlineformset_factory(VotingPoll, DateCandidate,
                                                  form=DateCandidateForm, formset=BaseCandidateFormSet, extra=1,
                                             can_delete=False)
    formset = date_candidateformset(prefix='form')
    form = DateForm()
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

            voters_undefined(poll)
            messages.success(request, _('Candidates successfully added!'))
            return redirect(reverse_lazy(date_candidate_create, kwargs={'pk': poll.pk}))

    return render(request, 'polls/date_candidate.html',
                  {'formset': formset,'form':form, 'poll': poll, 'candidates':candidates})


@login_required
@with_admin_rights
def delete_candidate(request, pk, cand):
    poll = get_object_or_404(VotingPoll, id=pk)
    candidate = get_object_or_404(Candidate, id=cand)
    candidate.delete()
    messages.success(request, _('Candidate has been deleted!'))
    return redirect(reverse_lazy(manage_candidate, kwargs={'pk': poll.id}))


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


@login_required
@with_admin_rights
def success(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)

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
                subject, from_email, to = 'invite to secret poll', 'whale4.ad@gmail.com', email
                htmly = get_template('polls/email.html')
                d = Context({'poll': poll, 'certi':certi})
                html_content = htmly.render(d)
                msg = EmailMessage(subject, html_content, from_email, [to])
                msg.content_subtype = "html"
                msg.send()

            messages.success(request, _('Inviters successfully added!'))
            return redirect(reverse_lazy(success, kwargs={'pk': poll.id}))
    else:
        form = InviteForm()
    return render(request, 'polls/success.html', locals())


@login_required
@with_admin_rights
def delete_anonymous(request,pk,voter):
    poll = get_object_or_404(VotingPoll, id=pk)
    voter = get_object_or_404(WhaleUserAnonymous, id=voter)
    if "user" in request.session:
        del request.session["user"]
    voter.delete()
    messages.success(request, _('anonymous voter has been deleted!'))
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
                messages.success(request, _(' your certificate is right '))
                request.session["user"] = str( user.id)
                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect(reverse_lazy('home'))

            except:
                messages.error (request, _(' your certificate is wrong'))
                return redirect(reverse_lazy('certificate', kwargs={'pk': poll.id}))

    return render(request, 'polls/certificate.html', locals())


@certificate_required
@status_required
def vote(request, pk):

    poll = get_object_or_404(VotingPoll, id=pk)
    candidates = ( DateCandidate.objects.filter(poll_id=poll.id) \
                       if poll.poll_type == 'Date'else Candidate.objects.filter(poll_id=poll.id))
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
        messages.info(request, _('you have already vote , now you can update your vote'))
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
            messages.success(request, _('Your vote has been added to the poll, thank you!'))
            if poll.option_ballots:
                return redirect(reverse_lazy(view_poll_secret, kwargs={'pk': poll.pk,'voter':voter.id}))
            elif poll.option_experimental:
                poll.status=False
                poll.save()
                return redirect(reverse_lazy('experimental'))
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
                v.save()
            messages.success(request, _('Your vote has been updated, thank you!'))
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
    messages.success(request, _('Your vote has been deleted!'))
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
    votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
    preference_model = preference_model_from_text(poll.preference_model,len(candidates))

    if poll.poll_type == 'Date':
        (days, months) = days_months(candidates)
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
            score = scores[id][c.id]
            tab[id]['scores'].append({
                'value': score,
                'class': 'poll-{0:d}percent'.format(int(round(preference_model.evaluate(score),
                                                              1) * 100)) if score != UNDEFINED_VALUE else 'poll-undefined',
                'text': preference_model.value2text(score) if score != UNDEFINED_VALUE else "?"


            })

    votes = None if tab == {} else tab.values()
    list1 = list()
    scores=[]
    if votes:
        for value in votes:
            v = dict()
            v['name'] = value['nickname']
            score= [val['value'] for val in value['scores']]
            v['values'] = score
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
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
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
    elif "result" in request.GET and request.GET['result']=='scoremethod':
        approval = dict()
        threshold = preference_model.len()
        approval["threshold"] = preference_model.values[1:]
        candi = []
        borda_scores = []
        plurality_scores = []
        veto_scores = []
        for i, c in enumerate(candidates):
            sum_borda = 0
            sum_plurality = 0
            sum_veto = 0

            for score in scores:
                sum_borda = sum_borda + (score[i] if score[i] != UNDEFINED_VALUE else 0)
                sum_plurality = sum_plurality + (1 if score[i] == preference_model.max() else 0)
                sum_veto = sum_veto + (1 if score[i] != (preference_model.min() or UNDEFINED_VALUE) else 0)
            candi.append(str(c))
            borda_scores.append(sum_borda)
            plurality_scores.append(sum_plurality)
            veto_scores.append(sum_veto)
        approval_scores = []
        for y in approval["threshold"]:
            th = []
            for i, c in enumerate(candidates):
                sum_approval = 0
                for score in scores:
                    sum_approval = sum_approval + (1 if score[i] >= y else 0)
                th.append(sum_approval)
            approval_scores.append(th)
        if preference_model.id == "rankingNoTies" or preference_model.id == "rankingWithTies":
            approval_scores.reverse()

        approval["scores"] = approval_scores

        score_method = dict()
        score_method["candidates"] = candi
        score_method["Borda"] = borda_scores
        score_method["Plurality"] = plurality_scores
        score_method["Veto"] = veto_scores
        score_method["Approval"] = approval
        return HttpResponse(json.dumps(score_method, indent=4, sort_keys=True), content_type="application/json")

    else:
        return render(request, 'polls/poll.html',locals() )


def result_view(request, pk ):
    poll = get_object_or_404(VotingPoll, id=pk)
    return render(request, 'polls/result.html', locals())


@login_required
@with_view_rights
def status(request, pk):
    poll = get_object_or_404(VotingPoll, id=pk)
    initial={'status':poll.status}
    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            poll.status = form.cleaned_data['status']
            poll.save()
            messages.success(request, _('Status successfully changed!'))
            return redirect(reverse_lazy(view_poll, kwargs={'pk': poll.id}))
    else:
        form = StatusForm(initial=initial)

        return render(request, 'polls/status_poll.html',locals())