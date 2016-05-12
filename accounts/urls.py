from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
from accounts.views import register
from polls.views import home


urlpatterns = patterns('',
    url(r'^login/$', auth_views.login, {'template_name': 'accounts/login.html'},name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'accounts/logout.html'}, name='logout'),
    url(r'^register/$', register.as_view(),name='register' ),
    url(r'^$',home, name='home'),
)

