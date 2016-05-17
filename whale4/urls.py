from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from polls.views import home
from django.conf.urls import ( handler400, handler403, handler404, handler500)

handler400 = 'whale4.views.bad_request'
handler403 = 'whale4.views.permission_denied'
handler404 = 'whale4.views.page_not_found'
handler500 = 'whale4.views.server_error'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^$',home, name='home'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

]

urlpatterns += staticfiles_urlpatterns()
