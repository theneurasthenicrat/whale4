from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^poll/(?P<id_poll>[a-f0-9]+)$', 'whale4.views.view_poll', name='poll'),
                       url(r'^$', 'whale4.views.home', name='home'),
                       url(r'^create-voting-poll/$', 'whale4.views.create_voting_poll', name='create voting poll'),
                       url(r'^add-candidate$', 'whale4.views.add_candidate', name='add candidate'),
                       # Examples:
                       # url(r'^blog/', include('blog.urls')),
                       
                       url(r'^admin/', include(admin.site.urls)),
)
