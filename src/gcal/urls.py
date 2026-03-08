from django.conf.urls import url

from gcal.views import sync_google_calendar, display

urlpatterns = [
    url('^sync/$', sync_google_calendar, name='sync_google_cal'),
    url('^display/(?P<month>[a-z]+)/$', display, name='display_month')
]
