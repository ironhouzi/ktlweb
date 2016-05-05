import httplib2
import os
import arrow
import json

from pytz import timezone

from apiclient import discovery
from oauth2client.client import SignedJwtAssertionCredentials

from django.utils.text import slugify as django_slugify
from django.utils.timezone import (
    get_default_timezone_name, utc, localtime, make_aware, is_naive)

from wagtail.wagtailcore.models import Page

from .models import Calendar, Centre, Event, EventPage

# TODO: check response codes!!!!!!!!!!!!!!!!!

SCOPES = os.environ.get(
    'GCAL_SCOPES',
    'https://www.googleapis.com/auth/calendar.readonly'
)


def slugify(string):
    string = string.lower()

    for substitution in (('æ', 'ae'), ('ø', 'oe'), ('å', 'aa'),):
        string = string.replace(*substitution)

    return django_slugify(string)


def get_credentials():
    '''
    Gets credentials for server to server google API communications.
    '''
    json_path = os.environ.get('JWT_JSON_PATH')

    if json_path:
        with open(json_path) as f:
            secrets = json.loads(f.read())
    else:
        secrets = {
            'client_email': os.environ['GCAL_CLIENT_MAIL'],
            'private_key': os.environ['GCAL_PRIVATE_KEY'].replace('\\n', '\n')
        }

    return SignedJwtAssertionCredentials(
        secrets['client_email'],
        secrets['private_key'],
        SCOPES
    )


def get_remote_calendars(service, items='id,summary,description,accessRole'):
    '''
    Fetches calendar list from Google Calendar API.
    '''
    return service.calendarList().list(
        fields='items({})'.format(items)).execute().get('items', [])


def create_event_instance_entry(gcal_event, event_page):
    # TODO: is it necessary to handle cancelled instance?
    start, end, full_day = json_time_to_utc(gcal_event)

    instance_data = dict(
        start=start,
        end=end,
        full_day=full_day,
        recurring_event_id=gcal_event.get('recurringEventId'),
        creator=gcal_event.get('creator'),
        event_page=event_page
    )

    event_instance_object, _ = Event.objects.update_or_create(
        event_id=gcal_event['id'],
        defaults=instance_data
    )

    event_instance_object.save()

    return event_instance_object


def fetch_instances(service, calendar, event_page):
    page_token = None

    while True:
        gcal_event_instances = service.events().instances(
            calendarId=calendar.calendar_id,
            eventId=event_page.first_event.event_id,
            pageToken=page_token
        ).execute()

        for gcal_event_instance in gcal_event_instances['items']:
            create_event_instance_entry(gcal_event_instance, event_page)

        page_token = gcal_event_instances.get('nextPageToken')

        # TODO: reassurance from infinite recurring events
        if page_token is None:
            break


def get_events(*args, **kwargs):
    '''
    Query events from Google calendar API.

    The query requires a calendarId, which can be derived either from a Google
    calendar query response object, or the local database.

    If the calendarId is derived locally, it should be provided as the second
    positional argument. If this function is used with a query response object,
    it should already be available in the kwargs as the query response object
    is a json dict.
    '''
    service, calendar = args

    if calendar:
        kwargs.setdefault('calendarId', calendar['id'])

    if kwargs.get('singleEvents'):
        kwargs.setdefault('orderBy', 'startTime')

    return service.events().list(**kwargs).execute()


def get_calendar_service():
    '''
    Helper function that returns a service object for the Google calendar API.
    '''
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    return discovery.build('calendar', 'v3', http=http)


def db_sync_calendars(service):
    '''
    Utility function for storing calendars from Google Calendar API to the
    local database.
    '''
    calendars = get_remote_calendars(service)

    for cal in calendars:
        if cal['accessRole'] != 'owner':
            continue

        center_code = cal['summary'].split('-')[0].rstrip()
        fk = Centre.objects.get(code=center_code)
        Calendar(
            calendar_id=cal['id'],
            summary=cal['summary'],
            description=cal['description'],
            public=cal['summary'].endswith('program'),
            centre=fk
        ).save()


def create_center(attributes, centre_parent_page):
    centre = None

    try:
        centre = Centre.objects.get(code=attributes['code'])
    except Page.DoesNotExist:
        centre = Centre(**attributes)
        centre_parent_page.add_child(instance=centre)


def update_or_create_event_page(event_data, event_id, centre_parent_page):
    event_page = EventPage.objects.filter(
        first_event__event_id=event_id
    )

    if event_page:
        event_page.update(**event_data)
        event_page = event_page[0]
    else:
        event_page = EventPage(**event_data)
        centre_parent_page.add_child(instance=event_page)

    return event_page


def register_centers():
    '''
    Utility function for registering the three available centres into the
    database.
    '''

    centre_parent_page = None

    try:
        centre_parent_page = Page.objects.get(title='sentre')
    except Page.DoesNotExist:
        centre_parent_page = Page(title='sentre', slug='sentre')
        site_root_page = Page.get_root_nodes()[0]
        site_root_page.add_child(instance=centre_parent_page)

    centres = (
        dict(
            code='KTL',
            slug='ktl',
            title='Karma Tashi Ling',
            address='Bjørnåsveien 124, 1272 Oslo',
            description='Vårt hovedsenter med tempelbygg og fredsstupa.',
            tlf='22 61 28 84'
        ),
        dict(
            code='PM',
            slug='pm',
            title='Paramita meditasjonssenter',
            address='Storgata 13, 0155 Oslo - 3 etasje (Strøget)',
            description='Vårt bysenter i gangavstand fra Oslo Sentralstasjon.',
            tlf='22 00 89 98'
        ),
        dict(
            code='KSL',
            slug='ksl',
            title='Karma Shedrup Ling retreatsenter',
            address='Siggerudveien 734, 1400 Ski',
            description='Retreatsenter i Sørmarka.',
            tlf=None
        ),
    )

    for centre_data in centres:
        create_center(centre_data, centre_parent_page)


def json_time_to_utc(gcal_event):
    '''
    Extracts a google calendar time range (start/stop) json object and returns
    a UTC datetime object and full-day boolean status.
    '''

    def to_utc(json_time, key, tz):
        '''
        json_time from google calendar API (RFC3339).
        key: 'date'/'dateTime'
        tz: timezone

        returns: UTC datetime objects
        '''
        time = arrow.get(json_time.get(key))

        # TODO: verify necessity of this check
        if is_naive(time):
            time = make_aware(time, timezone=tz)

        return localtime(time, utc)

    timerange = (gcal_event['start'], gcal_event['end'],)

    # TODO: verify that google calendar has sanity checked date/dateTime fields
    full_day = all(time.get('date') for time in timerange) and not (
               any(time.get('dateTime') for time in timerange))

    local_tz = timezone(timerange[0].get(
        'timeZone',
        timerange[1].get(
            'timeZone',
            get_default_timezone_name())
        )
    )

    key = 'date' if full_day else 'dateTime'
    start, end = (to_utc(time, key, local_tz) for time in timerange)

    # assert is_naive(start) and is_naive(end)
    return start, end, full_day


def create_event_page(calendar, gcal_event, events_root_page):
    recurrence = gcal_event.get('recurrence')

    if gcal_event['status'] == 'cancelled':
        # try:
        #     # TODO: elect new EventPage.first_entry
        #     gcal_event.objects.get(event_id=gcal_event['id']).delete()
        # except gcal_event.DoesNotExist:
        #     pass

        # # TODO: replace with Exception ??
        return (None, None,)

    title = gcal_event.get('summary', '')
    event_page_data = dict(
        title=title,
        slug=slugify(title),
        calendar=calendar,
        recurrence=recurrence,
        description=gcal_event.get('description', 'Ingen beskrivelse'),
        first_published_at=gcal_event['created']
    )

    event_page = update_or_create_event_page(
        event_page_data,
        gcal_event['id'],
        events_root_page
    )

    event_entry = create_event_instance_entry(gcal_event, event_page)
    event_page.first_event = event_entry

    return (recurrence, event_page,)


def db_sync_events(service, calendar, page_token):
    '''
    Update local database from Google Calendar API
    '''
    kwargs = {
        'calendarId': calendar.calendar_id,
        'syncToken': calendar.sync_token,
        'pageToken': page_token
    }

    calendar_data = get_events(service, None, **kwargs)
    next_page_token = calendar_data.get('nextPageToken')
    calendar.sync_token = calendar_data.get('nextSyncToken')
    calendar.save()

    events_parent_page = None

    try:
        events_parent_page = Centre.objects.get(code=calendar.centre.code)
    except Page.DoesNotExist:
        register_centers()
        events_parent_page = Centre.objects.get(code=calendar.centre.code)

    for gcal_event in calendar_data['items']:
        recurrence, event_page = create_event_page(
            calendar,
            gcal_event,
            events_parent_page
        )

        if recurrence is None and event_page is None:
            continue

        fetch_instances(service, calendar, event_page)

    return next_page_token


def db_sync_public_calendars(service):
    '''
    Synchronize all public calendars in local database.
    '''

    page_token = None

    for calendar in Calendar.objects.filter(public=True):
        while True:
            page_token = db_sync_events(service, calendar, page_token)

            if page_token is None:
                break


def db_init():
    '''
    Helper function for populating the local database.
    '''
    register_centers()
    service = get_calendar_service()
    db_sync_calendars(service)
    db_sync_public_calendars(service)


def sync_events():
    '''
    For CRONjobs or from a google API signal.

    Will update the calendars incrementally using the syncToken.
    '''
    service = get_calendar_service()
    db_sync_public_calendars(service)
