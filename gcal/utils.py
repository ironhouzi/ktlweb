import httplib2
import os
import arrow
import json
import logging
import datetime

from pytz import timezone

from apiclient import discovery
from oauth2client.client import SignedJwtAssertionCredentials

from django.contrib.auth.models import User
from django.utils.text import slugify as django_slugify
from django.utils.timezone import (
    get_default_timezone_name, utc, localtime, make_aware, is_naive)

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.rich_text import RichText

from .models import Calendar, Centre, Event, EventPage

# TODO: check response codes!!!!!!!!!!!!!!!!!

logger = logging.getLogger(__name__)

SCOPES = os.environ.get(
    'GCAL_SCOPES',
    'https://www.googleapis.com/auth/calendar.readonly'
)


def publish_page(page, page_parent, default_body_string, user):
    '''
    Helper function for publishing a manually created Wagtail Page object.
    '''

    logger.debug('publishing page: {} w/ parent: {}'.format(page, page_parent))

    paragraph = '<p>{}</p>'.format(default_body_string)

    page.body.stream_data = [
        ('paragraph', RichText(paragraph))
    ]

    page_parent.add_child(instance=page)

    revision = page.save_revision(
        user=user,
        submitted_for_moderation=False,
    )

    revision.publish()
    page.save()


def slugify(string):
    '''
    Helper function for converting Norwegian characters to ASCII representation.
    '''

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
    '''
    Function for creating event instance entries which belongs to an EventPage.
    '''

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

    logger.debug(
        'Created event instance w/ event id {}, master id: {})'
        .format(
            gcal_event['id'],
            event_page.first_event.event_id if event_page.first_event else None
        )
    )

    return event_instance_object


def fetch_instances(service, calendar, event_page):
    '''
    Populates the site with Google calendar events represented as EventPages
    with one or more event instances per EventPage.
    '''

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

        logger.info('Created calendar for: "{}"'.format(center_code))


def create_center(centre_data, centre_parent_page, user):
    '''
    Creates a Wagtail Page representing each centre. Note that there is one
    calendar per centre.
    '''

    centre_entry_data, description = centre_data
    centre = None

    try:
        Centre.objects.get(code=centre_entry_data['code'])
    except Centre.DoesNotExist:
        centre = Centre(show_in_menus=True, **centre_entry_data)
        publish_page(centre, centre_parent_page, description, user)


def update_or_create_event_page(event_data, event_id, centre_parent_page, user):
    event_data_attributes, event_description = event_data

    event_page = EventPage.objects.filter(
        first_event__event_id=event_id
    )

    if event_page:
        event_page.update(**event_data_attributes)
        event_page = event_page[0]
        action = 'Updated'
    else:
        event_page = EventPage(**event_data_attributes)
        publish_page(event_page, centre_parent_page, event_description, user)
        action = 'Created'

    logger.debug('{} event page for event id {}'.format(action, event_id))

    return event_page


def register_centers(user):
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
        main_page = site_root_page.get_children()[0]
        main_page.add_child(instance=centre_parent_page)

    centres = (
        (
            dict(
                code='KTL',
                slug='ktl',
                title='Karma Tashi Ling',
                address='Bjørnåsveien 124, 1272 Oslo',
                tlf='22 61 28 84'
            ),
            '<p>Vårt hovedsenter med tempelbygg og fredsstupa.</p>'
        ),
        (
            dict(
                code='PM',
                slug='pm',
                title='Paramita meditasjonssenter',
                address='Storgata 13, 0155 Oslo - 3 etasje (Strøget)',
                tlf='22 00 89 98'
            ),
            '<p>Vårt bysenter i gangavstand fra Oslo Sentralstasjon.</p>'
        ),
        (
            dict(
                code='KSL',
                slug='ksl',
                title='Karma Shedrup Ling retreatsenter',
                address='Siggerudveien 734, 1400 Ski',
                tlf=None
            ),
            '<p>Retreatsenter i Sørmarka.</p>'
        )
    )

    for centre_data in centres:
        create_center(centre_data, centre_parent_page, user)
        logger.info('registerred centre: "{}"'.format(centre_data[0]['title']))


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


def create_event_page(calendar, gcal_event, events_root_page, user):
    if gcal_event['status'] == 'cancelled':
        # try:
        #     # TODO: elect new EventPage.first_entry
        #     gcal_event.objects.get(event_id=gcal_event['id']).delete()
        # except gcal_event.DoesNotExist:
        #     pass

        # # TODO: replace with Exception ??
        return

    title = gcal_event.get('summary', '')
    event_page_data = (
        dict(title=title, slug=slugify(title), calendar=calendar),
        gcal_event.get('description', 'Ingen beskrivelse')
    )
    event_page = update_or_create_event_page(
        event_page_data,
        gcal_event['id'],
        events_root_page,
        user
    )

    event_entry = create_event_instance_entry(gcal_event, event_page)
    event_page.first_event = event_entry

    return event_page


def db_sync_events(service, calendar, page_token, user, recurring_events={}):
    '''
    Update local database from Google Calendar API
    '''
    today = datetime.datetime.utcnow().replace(
                hour=0,
                minute=0,
                second=0
            ).isoformat('T') + 'Z'

    kwargs = {
        'calendarId': calendar.calendar_id,
        'syncToken': calendar.sync_token,
        'singleEvents': True,
        'timeMin': today,
        'pageToken': page_token
    }

    calendar_data = get_events(service, None, **kwargs)
    next_page_token = calendar_data.get('nextPageToken')
    calendar.sync_token = calendar_data.get('nextSyncToken')
    calendar.save()

    events_parent_page = None
    logger.debug(
        'Saved into calendar "{}", sync token: "{}"'
        .format(calendar.calendar_id, calendar.sync_token)
    )

    try:
        events_parent_page = Centre.objects.get(code=calendar.centre.code)
    except Centre.DoesNotExist:
        register_centers(user)
        events_parent_page = Centre.objects.get(code=calendar.centre.code)

    for gcal_event in calendar_data['items']:
        if 'recurringEventId' in gcal_event:
            event_id = gcal_event['recurringEventId']

            if event_id not in recurring_events:
                recurring_events[event_id] = []

            recurring_events[event_id].append(gcal_event)
            logger.debug('Added to recurring events: "{}"'.format(event_id))
        else:
            # event_page = create_event_page(
            create_event_page(calendar, gcal_event, events_parent_page, user)

        # fetch_instances(service, calendar, event_page)

    return next_page_token, recurring_events


def create_recurring_event_pages(service, calendar, recurring_events, user):
    events_parent_page = Centre.objects.get(code=calendar.centre.code)

    for event_id, event_instances in recurring_events.items():
        event = service.events().get(
            calendarId=calendar.calendar_id,
            eventId=event_id,
        ).execute()

        event_page = create_event_page(
            calendar,
            event,
            events_parent_page,
            user
        )

        for event_instance in event_instances:
            create_event_instance_entry(event_instance, event_page)


def db_sync_public_calendars(service, user):
    '''
    Synchronize all public calendars in local database.
    '''

    for calendar in Calendar.objects.filter(public=True):
        recurring_events = {}
        page_token = None

        while True:
            page_token, recurring_events = db_sync_events(
                service, calendar, page_token, user, recurring_events
            )

            if page_token is None:
                break

        create_recurring_event_pages(service, calendar, recurring_events, user)


def get_user(user_name=None):
    '''
    Helper function to retreive User object from a username.
    '''

    if not user_name:
        raise RuntimeError('Must provide valid user name')

    user = User.objects.get(username=user_name)

    if user is None:
        raise RuntimeError('Username does not exist!')

    return user


def db_init(user_name=None):
    '''
    Helper function for populating the local database.
    '''

    user = get_user(user_name)

    register_centers(user)
    service = get_calendar_service()
    db_sync_calendars(service)
    db_sync_public_calendars(service, user)


def sync_events(user_name=None):
    '''
    For CRONjobs or from a google API signal.

    Will update the calendars incrementally using the syncToken.
    '''
    user = get_user(user_name)

    service = get_calendar_service()
    db_sync_public_calendars(service, user)
