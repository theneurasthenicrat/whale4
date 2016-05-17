from django.conf.urls import patterns, url
from accounts import views
from polls.views import home


urlpatterns = [
    url(r'^login/$', views.login_view,name='login'),
    url(r'^logout/$', views.logout_view,name='logout'),
    url(r'^register/$', views.register.as_view(), name='register'),
    url(r'^$', home, name='home'),
]
