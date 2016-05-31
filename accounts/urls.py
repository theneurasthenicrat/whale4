from django.conf.urls import patterns, url
from accounts import views
from polls.views import home


urlpatterns = [
    url(r'^login/$', views.login_view,name='login'),
    url(r'^logout/$', views.logout_view,name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^contact/$', views.ContactView.as_view(), name='contact'),
    url(r'^$', home, name='home'),
]
