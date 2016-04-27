# -*- coding: utf-8 -*-

# imports ####################################################################


# scoring ####################################################################

def scoring(votes, nb_candidates, pref_model,
            scoring = lambda x, pref_model: x, undefined = 0):
    """This function simply computes a score for each candidate, taking
    the scoring parameter as the scoring function (the list of values is
    necessary because some scoring vectors depend on the list of possible
    values / ranks. The parameter undefined just specifies the score given
    to each unranked candidate. nb_candidates is necessary in case votes is an
    empty list..."""

    scores = [0] * nb_candidates
    for v in votes:
        for i in range(0, len(v)):
            scores[i] += (undefined if v[i] == "undefined"
                          else scoring(v[i], pref_model))

    return scores

def borda(votes, nb_candidates, pref_model):
    return scoring(votes, nb_candidates, pref_model)

def plurality(votes, nb_candidates, pref_model):
    return scoring(votes, nb_candidates, pref_model,
                   scoring = lambda x, pref_model: 1 if x == pref_model.max else 0)

def veto(votes, nb_candidates, pref_model):
    return scoring(votes, nb_candidates, pref_model,
                   scoring = lambda x, pref_model: 0 if x == pref_model.min else 1)

def approval(votes, nb_candidates, pref_model, strict = True):
    return scoring(votes, nb_candidates, pref_model,
                   scoring = (lambda x, pref_model: (
                       1 if x > 0 or (not strict and x == 0) else 0)))



