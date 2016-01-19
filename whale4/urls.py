from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       # url(r'^poll/(?P<poll>[a-f0-9]+)$', 'whale4.views.view_poll', name='poll'),
                       url(r'^poll$', 'whale4.views.view_poll', name='poll'),
                       url(r'^$', 'whale4.views.home', name='home'),
                       url(r'^create-voting-poll/$', 'whale4.views.create_voting_poll', name='create voting poll'),
                       url(r'^manage-candidates$', 'whale4.views.manage_candidates', name='manage candidates'),
                       url(r'^delete-vote$', 'whale4.views.delete_vote', name='delete vote'),
                       url(r'^admin-poll$', 'whale4.views.admin_poll', name='administrate poll'),
                       url(r'^authenticate-admin$', 'whale4.views.authenticate_admin', name='authenticate admin'),
                       url(r'^vote$', 'whale4.views.vote', name='vote'),
                       # Examples:
                       # url(r'^blog/', include('blog.urls')),
                       
                       url(r'^admin/', include(admin.site.urls)),
)
