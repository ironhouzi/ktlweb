import httplib2
import os
import arrow
import json

from pytz import timezone

from apiclient import discovery
from oauth2client.client import SignedJwtAssertionCredentials

from .models import Calendar, Centre, Event
from django.utils.timezone import (
    get_default_timezone_name, utc, localtime, make_aware, is_naive, now)


# TODO: check response codes!!!!!!!!!!!!!!!!!

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


def get_credentials():
    '''
    Gets credentials for server to server google API communications.
    '''
    with open(os.environ['JWT_JSON_PATH']) as f:
        secrets = json.loads(f.read())

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

    kwargs.setdefault('timeMin', localtime(now()).isoformat())
    kwargs.setdefault('singleEvents', True)

    if kwargs['singleEvents']:
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


def register_centers():
    '''
    Utility function for registering the three available centres into the
    database.
    '''
    ktl = Centre(
        'KTL',
        'Karma Tashi Ling',
        'Bjørnåsveien 124, 1272 Oslo',
        'Vårt hovedsenter med tempelbygg og fredsstupa.',
        '22 61 28 84',
        None
    )

    ktl.save()

    pm = Centre(
        'PM',
        'Paramita meditasjonssenter',
        'Storgata 13, 0155 Oslo - 3 etasje (Strøget)',
        'Vårt bysenter i gangavstand fra Oslo Sentralstasjon.',
        '22 00 89 98',
        None
    )

    pm.save()

    ksl = Centre(
        'KSL',
        'Karma Shedrup Ling retreatsenter',
        'Siggerudveien 734, 1400 Ski',
        'Retreatsenter i Sørmarka.',
        None,
        None
    )

    ksl.save()


def json_time_to_utc(event):
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

    timerange = (event['start'], event['end'],)

    # TODO: verify that google calendar has sanity checked date/dateTime fields
    full_day = all(time.get('date') for time in timerange) and not (
               any(time.get('dateTime') for time in timerange))

    local_tz = timezone(timerange[0].get('timeZone',
        timerange[1].get('timeZone', get_default_timezone_name())))

    key = 'date' if full_day else 'dateTime'
    start, end = (to_utc(time, key, local_tz) for time in timerange)

    # assert is_naive(start) and is_naive(end)
    return start, end, full_day


def db_sync_events(service, calendar):
    '''
    Update local database from Google Calendar API
    '''
    kwargs = {
        'calendarId': calendar.calendar_id,
        'syncToken': calendar.sync_token
    }

    response = get_events(service, None, **kwargs)

    for event in response['items']:
        start, end, full_day = json_time_to_utc(event)

        db_event = Event(
            event_id=event['id'],
            start=start,
            end=end,
            summary=event.get('summary', ''),
            full_day=full_day,
            html_link=event.get('htmlLink'),
            calendar=calendar
        )

        db_event.save()

        calendar.sync_token = response.get('nextSyncToken')
        calendar.save()


def db_sync_public(service):
    '''
    Synchronize all public calendars in local database.
    '''

    for calendar in Calendar.objects.filter(public=True):
        db_sync_events(service, calendar)


def db_init():
    '''
    Helper function for populating the local database.
    '''
    register_centers()
    service = get_calendar_service()
    db_sync_calendars(service)
    db_sync_public(service)


def db_populate_events():
    '''
    Helper function for populating the local database.
    '''
    service = get_calendar_service()
    db_sync_public(service)
