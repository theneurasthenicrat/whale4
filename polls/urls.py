# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from polls import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^candidateCreate/(?P<pk>[^/]+)/$', views.candidateCreate, name='candidateCreate'),
    url(r'^dateCandidateCreate/(?P<pk>[^/]+)/$', views.dateCandidateCreate, name='dateCandidateCreate'),
    url(r'^updateVotingPoll/(?P<pk>[^/]+)/$', views.updateVotingPoll, name='updateVotingPoll'),
    url(r'^optionsCreate/(?P<pk>[^/]+)/$', views.optionsCreate, name='optionsCreate'),
    url(r'^deleteCandidate/(?P<pk>[^/]+)/(?P<cand>[^/]+)/$', views.deleteCandidate, name='deleteCandidate'),
    url(r'^updateVote/(?P<pk>[^/]+)/(?P<voter>[^/]+)/$', views.updateVote, name='updateVote'),
    url(r'^deleteVote/(?P<pk>[^/]+)/(?P<voter>[^/]+)/$', views.deleteVote, name='deleteVote'),
    url(r'^newPoll/$', views.votingPollCreate,name='newPoll'),
    url(r'^viewPoll/(?P<pk>[^/]+)/$', views.viewPoll, name='viewPoll'),
    url(r'^vote/(?P<pk>[^/]+)/$', views.vote, name='vote'),
]