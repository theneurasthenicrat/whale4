from django.urls import re_path
from accounts import views
from polls.views import home
from django.contrib.auth import views as auth_views

uuid4 = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
urlpatterns = [
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^register/$', views.Register.as_view(), name='register'),
    re_path(r'^contact/$', views.ContactView.as_view(), name='contact'),
    re_path(r'^$', home, name='home'),
    re_path(r'^accountPoll/(?P<pk>' + uuid4 + ')/$', views.WhaleUserDetail.as_view(), name='accountPoll'),
    re_path(r'^password/$', views.change_password, name='change_password'),
    re_path(r'^password_reset/$', views.password_reset, name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
