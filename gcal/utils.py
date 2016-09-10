import httplib2
import os
import arrow
import json
import logging
import datetime
import warnings

from pytz import timezone

from apiclient import discovery
from apiclient.errors import HttpError
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


class ExpiredGoogleCalendarSyncToken(Exception):
    pass


def publish_page(page, page_parent, default_body_string, user):
    '''
    Helper function for publishing a manually created Wagtail Page object.
    '''

    logger.debug('publishing page: {}'.format(page))

    paragraph = '<p>{}</p>'.format(default_body_string)

    page.body.stream_data = [
        ('paragraph', RichText(paragraph))
    ]

    # only set page parent if handling newly created page
    # if page_parent is not None:
    if page.get_parent() is None:
        logger.debug('Set parent: {} for {}'.format(page_parent, page))
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


def sync_event_instance_entry(gcal_event, event_page):
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
        event_page=event_page
    )

    event_instance_object, _ = Event.objects.update_or_create(
        event_id=gcal_event['id'],
        defaults=instance_data
    )

    event_instance_object.save()

    return event_instance_object


def poll_events(service, calendar, page_token):
    '''
    Request event list from Google calendar API.

    Input:
        service - google calendar service instance.
        kwargs dict - get events list request parameters.
    Output:
        tuple - (response, next page token, next sync token).
    '''

    gcal_params = {
        'calendarId': calendar.calendar_id,
    }

    if page_token is not None:
        gcal_params['pageToken'] = page_token

    if calendar.sync_token is None:
        # Create all events from scratch

        iso_time_today = datetime.datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ).isoformat('T') + 'Z'

        gcal_params.update({
            'singleEvents': True,
            'timeMin': iso_time_today
        })

    else:
        # perform partial event sync

        gcal_params['syncToken'] = calendar.sync_token

    logger.debug('List events w/ params: {}'.format(gcal_params))

    try:
        response = service.events().list(**gcal_params).execute()
    except HttpError as http_err:
        if http_err.error.resp.status == 401:
            logger.debug('Google sync token expired!')
            raise ExpiredGoogleCalendarSyncToken
        else:
            raise http_err

    next_page_token = response.get('nextPageToken')
    next_sync_token = response.get('nextSyncToken')

    if next_page_token is None and next_sync_token is None:
        warnings.warn(
            'Inconsistent Google calendar response: No tokens received!',
            ResourceWarning
        )
    elif next_page_token is not None and next_sync_token is not None:
        warnings.warn(
            'Inconsistent Google calendar response: '
            'Received both page token and sync token!',
            ResourceWarning
        )

    logger.debug(
        'returned {} items (page_token is {}, next_sync_token is {})'.format(
            len(response['items']), next_page_token, next_sync_token
        )
    )

    return response


def get_calendar_service():
    '''
    Helper function that returns a service object for the Google calendar API.
    '''

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    return discovery.build('calendar', 'v3', http=http)


def create_db_calendars(service):
    '''
    Utility function for storing calendars from Google Calendar API to the
    local database.
    '''

    calendars = get_remote_calendars(service)

    for cal in calendars:
        if cal['accessRole'] != 'owner':
            continue

        # Assumes the pertinent calendar names are formed as:
        # "<Centre code> - Program"
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
        initial_event__event_id=event_id
    )

    if event_page:
        event_page.update(**event_data_attributes)
        event_page = event_page[0]
        action = 'Updated'
    else:
        event_page = EventPage(**event_data_attributes)
        action = 'Created'

    publish_page(event_page, centre_parent_page, event_description, user)

    logger.debug('{} event page for event id {}'.format(action, event_id))

    return event_page


def register_centers(user):
    '''
    Utility function for registering the three available centres into the
    database.
    '''

    centre_parent_page = None

    try:
        centre_parent_page = Centre.objects.get(title='sentre')
    except Centre.DoesNotExist:
        centre_parent_page = Centre(
            title='sentre',
            slug='sentre',
            show_in_menus=True
        )
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
            'Vårt hovedsenter med tempelbygg og fredsstupa.'
        ),
        (
            dict(
                code='PM',
                slug='pm',
                title='Paramita meditasjonssenter',
                address='Storgata 13, 0155 Oslo - 3 etasje (Strøget)',
                tlf='22 00 89 98'
            ),
            'Vårt bysenter i gangavstand fra Oslo Sentralstasjon.'
        ),
        (
            dict(
                code='KSL',
                slug='ksl',
                title='Karma Shedrup Ling retreatsenter',
                address='Siggerudveien 734, 1400 Ski',
                tlf=None
            ),
            'Retreatsenter i Sørmarka.'
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


def handle_cancelled_event(event):
    # cases:
    # 1. deleted recurring event instance
    # 2. deleted recurring event instance which is event_page initial_event
    # 3. deleted non-recurring event
    #
    #
    # try:
    #     # TODO: elect new EventPage.initial_event
    #     main_gcal_event.objects.get(event_id=main_gcal_event['id']).delete()
    # except main_gcal_event.DoesNotExist:
    #     pass

    logger.debug('Handling cancelled event: {}'.format(event['summary']))

    cancelled_event = Event.objects.get(event_id=event['id'])
    event_page = cancelled_event.event_page
    needs_new_initial_event = event_page.initial_event == cancelled_event

    cancelled_event.delete()

    if len(event_page.event_instances) == 0:
        event_page.delete()
    elif needs_new_initial_event:
        # event_page.initial_event = event_page.event_instances
        pass

    logger.debug('compute_events created event page: "{}"'.format(event))


def sync_event_page(calendar, main_gcal_event, user):
    title = main_gcal_event.get('summary', '')
    event_page_data = (
        dict(
            title=title,
            slug=slugify(title),
            recurrence=main_gcal_event.get('recurrence'),
            creator=main_gcal_event.get('creator'),
            calendar=calendar
        ),
        main_gcal_event.get('description', 'Ingen beskrivelse')
    )

    try:
        event_parent_page = Centre.objects.get(code=calendar.centre.code)
    except Centre.DoesNotExist:
        register_centers(user)
        event_parent_page = Centre.objects.get(code=calendar.centre.code)

    event_page = update_or_create_event_page(
        event_page_data,
        main_gcal_event['id'],
        event_parent_page,
        user
    )

    event_entry = sync_event_instance_entry(main_gcal_event, event_page)
    event_page.initial_event = event_entry
    event_page.save()

    logger.debug(
        'compute_events created event page for single event: "{}" ({})'
        .format(main_gcal_event['id'], main_gcal_event.get('summary'))
    )

    return event_page


def compute_events(service, calendar, page_token, user, recurring_events={}):
    '''
    Used to create calendar events in the database.

    Collects events from Google Calendar using the 'singleEvents'
    parameters, which will expand all event instances into single events. Any
    recurring event will be collected in the `recurring_events` dictionary using
    the main event id as the key and a list of event ids as the value. The
    dictionary is used by sync_recurring_events().

    If an event does not contain a recurringEventId, it is a non-recurring event
    and the EventPage representing the event can be created immediately.

    A page_token is used to support pagination with Google Calendar, which will
    break up a huge response into smaller responses. The token will be `None`
    when the all the data has been transmitted.
    '''

    events_response = poll_events(service, calendar, page_token)

    next_page_token = events_response.get('nextPageToken')
    sync_token = events_response.get('nextSyncToken')

    # Only the last paginated response contains a nextSyncToken
    if next_page_token is None and sync_token is not None:
        calendar.sync_token = sync_token
        calendar.save()

        logger.debug(
            'Saved into calendar "{}", sync token: "{}"'
            .format(calendar.calendar_id, calendar.sync_token)
        )

    for gcal_event in events_response['items']:
        if gcal_event.get('status') == 'cancelled':
            handle_cancelled_event(gcal_event)
        elif 'recurringEventId' in gcal_event:
            main_event_id = gcal_event['recurringEventId']

            if main_event_id not in recurring_events:
                recurring_events[main_event_id] = []

            recurring_events[main_event_id].append(gcal_event)

            logger.debug(
                'compute_events added recurrence {} to event: "{}" ({})'
                .format(
                    gcal_event['id'],
                    main_event_id,
                    gcal_event.get('summary')
                )
            )
        else:
            sync_event_page(calendar, gcal_event, user)

    return next_page_token, recurring_events


def sync_recurring_events(service, calendar, recurring_events, user):
    '''
    Iterates key-values in recurring_events dictionary. From the key, creating
    a Wagtail EventPage based on a Google Calendar get-event request. From the
    value, all recurring instances in the value list will also be created as
    Event entries in the database.
    '''

    events_parent_page = Centre.objects.get(code=calendar.centre.code)

    for main_event_id, event_instances in recurring_events.items():
        event = service.events().get(
            calendarId=calendar.calendar_id,
            eventId=main_event_id,
        ).execute()

        event_page = sync_event_page(
            calendar,
            event,
            events_parent_page,
            user
        )

        for event_instance in event_instances:
            sync_event_instance_entry(event_instance, event_page)


def sync_db_calendar_events(service, user):
    '''
    Synchronize all public calendars in local database.
    '''

    for calendar in Calendar.objects.filter(public=True):
        recurring_events = {}
        next_page_token = None

        while True:
            try:
                next_page_token, recurring_events = compute_events(
                    service,
                    calendar,
                    next_page_token,
                    user,
                    recurring_events
                )
            except ExpiredGoogleCalendarSyncToken:
                logger.debug('Sync token EXPIRED!')
                logger.debug('Removing sync token and event data ..')
                calendar.sync_token = None
                Event.objects.all().delete()
                EventPage.objects.all().delete()

                # leave except block without breaking while loop
                next_page_token = True

            if next_page_token is None:
                break

        sync_recurring_events(service, calendar, recurring_events, user)


def get_user(user_name):
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

    service = get_calendar_service()
    register_centers(user)
    create_db_calendars(service)
    sync_db_calendar_events(service, user)


def sync_events(user_name=None):
    '''
    For CRONjobs or from a google API signal.

    Will update the calendars incrementally using the syncToken.
    '''
    user = get_user(user_name)
    service = get_calendar_service()
    sync_db_calendar_events(service, user)
