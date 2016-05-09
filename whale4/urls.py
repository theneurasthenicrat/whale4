from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from accounts.views import RegistrationView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls')),
    url(r'^poll$', 'whale4.views.view_poll', name='poll'),
    url(r'^$', 'polls.views.home', name='home'),
    url(r'^create-voting-poll/$', 'whale4.views.create_voting_poll', name='create voting poll'),
    url(r'^manage-candidates$', 'whale4.views.manage_candidates', name='manage candidates'),
    url(r'^delete-vote$', 'whale4.views.delete_vote', name='delete vote'),
    url(r'^admin-poll$', 'whale4.views.admin_poll', name='administrate poll'),
    url(r'^vote$', 'whale4.views.vote', name='vote'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'accounts/logout.html'}, name='logout'),
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    url(r'^register-success/$', 'accounts.views.register_success', name='register-success'),
    
]

urlpatterns += staticfiles_urlpatterns()