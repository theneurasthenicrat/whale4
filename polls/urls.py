# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from polls import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^candidateCreate/(?P<pk>[^/]+)/$', views.candidate_create, name='candidateCreate'),
    url(r'^dateCandidateCreate/(?P<pk>[^/]+)/$', views.date_candidate_create, name='dateCandidateCreate'),
    url(r'^manageCandidate/(?P<pk>[^/]+)/$', views.manage_candidate, name='manageCandidate'),
    url(r'^updateVotingPoll/(?P<pk>[^/]+)/$', views.VotingPollUpdate.as_view(), name='updateVotingPoll'),
    url(r'^deleteCandidate/(?P<pk>[^/]+)/(?P<cand>[^/]+)/$', views.delete_candidate, name='deleteCandidate'),
    url(r'^updateVote/(?P<pk>[^/]+)/(?P<voter>[^/]+)/$', views.update_vote, name='updateVote'),
    url(r'^deleteVote/(?P<pk>[^/]+)/(?P<voter>[^/]+)/$', views.delete_vote, name='deleteVote'),
    url(r'^newPoll/$', views.VotingPollCreate.as_view(), name='newPoll'),
    url(r'^viewPoll/(?P<pk>[^/]+)/$', views.view_poll, name='viewPoll'),
    url(r'^vote/(?P<pk>[^/]+)/$', views.vote, name='vote'),
    url(r'^success/(?P<pk>[^/]+)/$', views.success, name='success'),
    url(r'^admin/(?P<pk>[^/]+)/$', views.admin_poll, name='admin'),
]
