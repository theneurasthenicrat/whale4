

from django.shortcuts import get_object_or_404
import json
from polls.models import VotingScore, VotingPoll,\
    Candidate, DateCandidate, UNDEFINED_VALUE, preference_model_from_text
from accounts.models import User

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
    list_voters = []
    for i in voters:
        if i not in list_voters:
            list_voters.append(i)
    if voters:
        initial_candidates = VotingScore.objects.values_list('candidate', flat=True).filter(
            candidate__poll__id=poll.id).distinct()
        final_candidates = Candidate.objects.values_list('id', flat=True).filter(poll_id=poll.id)
        candidates_diff = list(set(final_candidates).difference(initial_candidates))

        for c in candidates_diff:
            c = get_object_or_404(Candidate, id=c)
            for voter in list_voters:
                voter = get_object_or_404(User, id=voter)
                VotingScore.objects.create(candidate=c, voter=voter, value=UNDEFINED_VALUE)


def poll_as_dict(poll):
    """Serializes a poll as a dictionnary.

    Arguments:
    poll -- the poll to be serialized"""
    poll_dict = {}
    candidates = poll.candidate_list()
    poll_dict['candidates'] = candidates
    preference_model = preference_model_from_text(poll.preference_model, len(candidates))
    poll_dict['preferenceModel'] = preference_model.as_dict_option() if poll.option_choice\
                                   else preference_model.as_dict()
    poll_dict['type'] = 1 if poll.poll_type == 'Date' else 0
    poll_dict['votes'] = []
    for vote in poll.voting_profile():
        poll_dict['votes'].append({'name': vote['voter'].nickname, 'values': vote['scores']})
    return poll_dict

def dump_polls_as_json(filename='polls/data.json'):
    """Dumps all the polls in JSON format.

    This function retrieves all the polls from the database
    and dumps them in JSON format in a file. This function
    is intended to be run periodically to provide a snapshot
    of the database.

    Keyword arguments:
    filename -- the file name in which it should be dumped (default: 'polls/data.json')"""
    polls = VotingPoll.objects.all()
    polls_dict = []
    for poll in polls:
        polls_dict.append(poll_as_dict(poll))

    with open(filename, 'w') as outfile:
        json.dump(polls_dict, outfile, indent=4, sort_keys=True)
