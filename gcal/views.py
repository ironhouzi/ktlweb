from wagtail.wagtailadmin import messages
from django.shortcuts import redirect

from .utils import sync_events


def sync_google_calendar(request):
    sync_events(request.user)
    messages.success(request, 'Kalender er synkronisert!')

    return redirect('wagtailadmin_home')
