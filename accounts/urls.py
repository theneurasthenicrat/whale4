from django.conf.urls import patterns, url
from accounts import views
from polls.views import home


urlpatterns = [
    url(r'^login/$', views.login_view,name='login'),
    url(r'^logout/$', views.logout_view,name='logout'),
    url(r'^Register/$', views.Register.as_view(), name='Register'),
    url(r'^$', home, name='home'),
]
