
from django.shortcuts import get_object_or_404
import json
from polls.models import VotingScore, VotingPoll,\
    Candidate, DateCandidate, UNDEFINED_VALUE, preference_model_from_text
from accounts.models import WhaleUser

# simple functions ######################################################################


def days_months(candidates):
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


def voters_undefined(poll):
    voters = VotingScore.objects.values_list('voter', flat=True).filter(candidate__poll__id=poll.id).distinct()
    if voters:
        initial_candidates = VotingScore.objects.values_list('candidate', flat=True).filter(
            candidate__poll__id=poll.id).distinct()
        final_candidates = Candidate.objects.values_list('id', flat=True).filter(poll_id=poll.id)
        candidates_diff = list(set(final_candidates).difference(initial_candidates))

        for c in candidates_diff:
            c = get_object_or_404(Candidate, id=c)
            for voter in voters:
                voter = get_object_or_404(WhaleUser, id=voter)
                VotingScore.objects.create(candidate=c, voter=voter, value=UNDEFINED_VALUE)


def data_poll():
    polls = VotingPoll.objects.all()
    json_polls = dict()
    for i, poll in enumerate(polls):
        json_object = dict()
        candidates = (
            DateCandidate.objects.filter(
                poll_id=poll.id) if poll.poll_type == 'Date'else Candidate.objects.filter(
                poll_id=poll.id))
        votes = VotingScore.objects.filter(candidate__poll__id=poll.id)
        preference_model = preference_model_from_text(poll.preference_model, len(candidates))
        scores = {}
        for v in votes:
            if v.voter.id not in scores:
                scores[v.voter.id] = {}
            scores[v.voter.id][v.candidate.id] = v.value
        tab = {}
        for v in votes:
            id = v.voter.id
            tab[id] = []
            for c in candidates:
                tab[id].append(scores[id][c.id])

        json_object[
            'preferenceModel'] = preference_model.as_dict_option() if poll.option_choice else preference_model.as_dict()
        json_object['type'] = 1 if poll.poll_type == 'Date' else 0
        json_object['candidates'] = ['candidate' + str(i + 1) for i, c in enumerate(candidates)]
        json_object['votes'] = [('voter' + str(i + 1), score) for i, score in enumerate(tab.values())]
        json_polls['poll' + str(i + 1)] = json_object

    with open('polls/data.json', 'w') as outfile:
        json.dump(json_polls, outfile, indent=4, sort_keys=True)
