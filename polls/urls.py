# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from polls import views

uuid4="[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^choice$', views.choice, name='choice'),
    url(r'^candidateCreate/(?P<pk>'+uuid4+')/$', views.candidate_create, name='candidateCreate'),
    url(r'^dateCandidateCreate/(?P<pk>'+uuid4+')/$', views.date_candidate_create, name='dateCandidateCreate'),
    url(r'^manageCandidate/(?P<pk>'+uuid4+')/$', views.manage_candidate, name='manageCandidate'),
    url(r'^updateVotingPoll/(?P<pk>'+uuid4+')/$', views.VotingPollUpdate.as_view(), name='updateVotingPoll'),
    url(r'^deleteCandidate/(?P<pk>'+uuid4+')/(?P<cand>[^/]+)/$', views.delete_candidate, name='deleteCandidate'),
    url(r'^updateVote/(?P<pk>'+uuid4+')/(?P<voter>'+uuid4+')/$', views.update_vote, name='updateVote'),
    url(r'^deleteVote/(?P<pk>'+uuid4+')/(?P<voter>'+uuid4+')/$', views.delete_vote, name='deleteVote'),
    url(r'^newPoll/(?P<choice>[^/]+)/$', views.VotingPollCreate.as_view(), name='newPoll'),
    url(r'^accountPoll/(?P<pk>'+uuid4+')/$', views.WhaleUserDetail.as_view(), name='accountPoll'),
    url(r'^viewPoll/(?P<pk>'+uuid4+')/$', views.view_poll, name='viewPoll'),
    url(r'^vote/(?P<pk>'+uuid4+')/(?P<user>'+uuid4+')/$', views.vote, name='vote'),
    url(r'^success/(?P<pk>'+uuid4+')/$', views.success, name='success'),
    url(r'^admin/(?P<pk>'+uuid4+')/$', views.admin_poll, name='admin'),
    url(r'^option/(?P<pk>'+uuid4+')/$', views.option, name='option'),
    url(r'^deleteVotingPoll/(?P<pk>'+uuid4+')/$', views.voting_poll_delete, name='deleteVotingPoll'),
    url(r'^pollJson/(?P<pk>'+uuid4+')/$', views.view_poll_json, name='pollJson'),
    url(r'^pollcsv/(?P<pk>'+uuid4+')/$', views.view_poll_csv, name='pollCsv'),
    url(r'^certificate/(?P<pk>'+uuid4+')/$', views.certificate, name='certificate'),
    url(r'^manageVote/(?P<pk>'+uuid4+')/$', views.manage_vote, name='manageVote'),
]
