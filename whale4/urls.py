from django.urls import  include, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from polls.views import home
from django.conf.urls import handler400,handler403,handler404,handler500

handler400 = 'polls.views.bad_request'
handler403 = 'polls.views.permission_denied'
handler404 = 'polls.views.page_not_found'
handler500 = 'polls.views.server_error'

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^polls/', include('polls.urls')),
    re_path(r'^accounts/', include('accounts.urls')),
    re_path(r'^$',home, name='home'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),


]

urlpatterns += staticfiles_urlpatterns()

