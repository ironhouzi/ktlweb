from django.urls import re_path

from gcal.views import sync_google_calendar, display

urlpatterns = [
    re_path('^sync/$', sync_google_calendar, name='sync_google_cal'),
    re_path('^display/(?P<month>[a-z]+)/$', display, name='display_month'),
]
