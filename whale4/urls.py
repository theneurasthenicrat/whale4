from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from polls.views import home

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^$',home, name='home'),

]

urlpatterns += staticfiles_urlpatterns()