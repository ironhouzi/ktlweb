from django.conf.urls import url

from .views import sync_google_calendar

urlpatterns = [url('^sync/$', sync_google_calendar, name='sync_google_cal')]
