from collections import OrderedDict
from django import template
from django.utils.timezone import now as django_now
from gcal.models import Event, Centre


register = template.Library()


@register.inclusion_tag('gcal/tags/upcoming_events.html')
def show_upcoming_events(count, centre_code, display_all):
    if count is not None:
        count = min(max(1, int(count)), 10)

    now = django_now()

    try:
        centre = Centre.objects.get(code=centre_code)
        title = 'Kommende aktiviteter på {}'.format(centre.title)

        events = centre.events.filter(end__gte=now).order_by('start')
    except Centre.DoesNotExist:
        centre = None
        title = 'Kommende aktiviteter'

        events = Event.objects.filter(end__gte=now).order_by('start')

    grouped = OrderedDict()

    for event in events:
        key = event.start.strftime('%B')

        try:
            grouped[key].append(event)
        except KeyError:
            grouped[key] = []
            grouped[key].append(event)

    return {
        'events': events[:count],
        'count': len(events),
        'title': title,
        'full': grouped,
        'display_all': display_all
    }


@register.inclusion_tag('gcal/tags/upcoming_events.html')
def show_event_instances(count, event_page):
    if count is not None:
        count = min(max(1, int(count)), 10)

    now = django_now()

    events = event_page.event_instances.filter(
        end__gte=now
    ).order_by('start')[:count]

    return {
        'events': events,
        'centre': event_page.calendar.centre,
        'title': 'Kommende aktiviteter'
    }


@register.inclusion_tag('gcal/tags/full_event_overview.html')
def full_event_overview(event_page):
    overview = OrderedDict()
    now = django_now()

    events = event_page.event_instances.filter(end__gte=now).order_by('start')

    if events.count() <= 3:
        return {}

    for event in events:
        month = event.start.strftime('%B')

        try:
            overview[month].append(event)
        except KeyError:
            overview[month] = [event]

    return {'result': overview}
