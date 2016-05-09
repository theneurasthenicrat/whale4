# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from polls.views import VotingPollCreate

urlpatterns = patterns('polls.views',
	url(r'^$','home',name='home'),
	url(r'^candidateCreate/(?P<pk>[^/]+)/$', 'candidateCreate',name='candidateCreate'),
	url(r'^newPoll/$', VotingPollCreate.as_view()),
	url(r'^viewPoll/(?P<pk>[^/]+)/$', 'viewPoll',name='viewPoll'),
)