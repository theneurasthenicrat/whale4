from django.conf.urls import url
from accounts import views
from polls.views import home
from django.contrib.auth import views as auth_views

uuid4 = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^contact/$', views.ContactView.as_view(), name='contact'),
    url(r'^$', home, name='home'),
    url(r'^accountPoll/(?P<pk>' + uuid4 + ')/$', views.WhaleUserDetail.as_view(), name='accountPoll'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]
