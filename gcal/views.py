from datetime import datetime
from wagtail.wagtailadmin import messages
from django.shortcuts import redirect, render

from gcal.utils import sync_events
from gcal.models import Event


def sync_google_calendar(request):
    sync_events(request.user)
    messages.success(request, 'Kalender er synkronisert!')

    return redirect('wagtailadmin_home')


def display(request, month):
    month_number = datetime.strptime(month, '%B').month
    return render(
        request,
        'gcal/display_month.html',
        {
            'month': month,
            'events': Event.objects.filter(start__month=month_number)
        }
    )
