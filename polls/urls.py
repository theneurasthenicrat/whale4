# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView
from polls import views

uuid4="[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^redirectPage/$', views.redirect_page, name='redirectPage'),
    url(r'^choosePollType$', views.choose_poll_type, name='choosePollType'),
    url(r'^candidateCreate/('+uuid4+')/$', views.candidate_create, name='candidateCreate'),
    url(r'^dateCandidateCreate/('+uuid4+')/$', views.date_candidate_create, name='dateCandidateCreate'),
    url(r'^manageCandidate/('+uuid4+')/$', views.manage_candidate, name='manageCandidate'),
    url(r'^updatePoll/(' + uuid4 +')/$', views.update_voting_poll, name='updatePoll'),
    url(r'^deleteCandidate/('+uuid4+')/([^/]+)/$', views.delete_candidate, name='deleteCandidate'),
    url(r'^updateVote/('+uuid4+')/([^/]+)/$', views.update_vote, name='updateVote'),
    url(r'^deleteVote/('+uuid4+')/([^/]+)/$', views.delete_vote, name='deleteVote'),
    url(r'^deleteAnonymous/('+uuid4+')/([^/]+)/$', views.delete_anonymous, name='deleteAnonymous'),
    url(r'^newPoll/(?P<choice>[^/]+)/$', views.new_poll, name='newPoll'),
    url(r'^viewPoll/('+uuid4+')', views.view_poll, name='viewPoll'),
    url(r'^status/('+uuid4+')', views.status, name='status'),
    url(r'^viewPollSecret/('+uuid4+')/([^/]+)/$', views.view_poll_secret, name='viewPollSecret'),
    url(r'^vote/('+uuid4+')', views.vote, name='vote'),
    url(r'^invitation/('+uuid4+')/$', views.invitation, name='invitation'),
    url(r'^admin/('+uuid4+')/$', views.admin_poll, name='admin'),
    url(r'^resetPoll/('+uuid4+')/$', views.reset_poll, name='resetPoll'),
    url(r'^advancedParameters/('+uuid4+')/$', views.advanced_parameters, name='advancedParameters'),
    url(r'^deleteVotingPoll/(' + uuid4 +')/$', views.delete_poll, name='deleteVotingPoll'),
    url(r'^certificate/('+uuid4+')', views.certificate, name='certificate'),
    url(r'^results/('+uuid4+')', views.result_all, name='results'),
    url(r'^viewResult/('+uuid4+')/([^/]+)/$', views.result_view, name='viewResult'),
    url(r'^scores/('+uuid4+')/([^/]+)/$', views.result_scores, name='scores'),
    url(r'^data/('+uuid4+')', views.data_page, name='data'),
    url(r'^allData$', TemplateView.as_view(template_name='polls/all_data.html'), name='allData'),
    url(r'^about$', TemplateView.as_view(template_name='polls/about.html'), name='about'),


]
