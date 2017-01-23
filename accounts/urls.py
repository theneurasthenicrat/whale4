from django.conf.urls import url
from accounts import views
from polls.views import home

uuid4="[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^contact/$', views.ContactView.as_view(), name='contact'),
    url(r'^$', home, name='home'),
    url(r'^accountPoll/(' + uuid4 + ')/$', views.WhaleUserDetail.as_view(), name='accountPoll'),
]
