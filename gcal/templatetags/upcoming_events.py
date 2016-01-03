from django import template
from django.db.models import Q
from django.utils.timezone import now as django_now
from gcal.models import Event


from datetime import datetime


register = template.Library()


@register.inclusion_tag('gcal/tags/upcoming_events.html')
def show_upcoming_events(count):
    # TODO: catch exception for int()
    count = min(max(1, int(count)), 10)
    now = django_now()

    return {
        'events': Event.objects.filter(
           Q(start__gte=now) | Q(end__gte=now)).order_by('start')[:count]
    }
