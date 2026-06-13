import datetime as dt
import os
import json
import logging
import string
import warnings

from uuid import uuid4

from apiclient import discovery
from apiclient.errors import HttpError
from google.oauth2.service_account import Credentials

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.text import slugify as django_slugify

from wagtail.models import Page
from wagtail.rich_text import RichText

from .models import Calendar, Centre, Event, EventPage
from home.models import HomePage
from ktlweb.settings.base import DEBUG_DATE_SKEW

logger = logging.getLogger(__name__)

CENTRES = (
    (
        dict(
            code='KTL',
            slug='ktl',
            title='Karma Tashi Ling',
            address='Bjørnåsveien 124, 1272 Oslo',
            # get from map embed URI
            map_query=(
                'pb=!1m18!1m12!1m3!1d64085.02466250845!2d10.719858097203817'
                '!3d59.8714410155457!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.'
                '1!3m3!1m2!1s0x4641689e9e629ca3%3A0x659a4f081752df6d!2s'
                'Karma+Tashi+Ling+buddhistsamfunn!5e0!3m2!1sen!2sus'
                '!4v1474500703908'
            ),
            tlf='22 61 28 84'
        ),
        'Vårt hovedsenter med tempelbygg og fredsstupa.'
    ),
    (
        dict(
            code='OB',
            slug='ob',
            title='Oslo Buddhistsenter',
            address='Helgesensgate 10, 0553 Oslo',
            # get from map embed URI
            map_query=(
                'pb=!1m18!1m12!1m3!1d1999.449835712254!2d10.755166416239534'
                '!3d59.92467757018657!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13'
                '.1!3m3!1m2!1s0x46416e62150dc545%3A0x1a4ccc594f09125a!2sOsl'
                'o%20Buddhist%20Center!5e0!3m2!1sen!2sno!4v1657655861752!5m'
                '2!1sen!2sno'
            ),
            tlf=None
        ),
        'Bysenter.'
    ),
    (
        dict(
            code='KSL',
            slug='ksl',
            title='Karma Shedrup Ling retreatsenter',
            # get from map embed URI
            map_query=(
                'pb=!1m18!1m12!1m3!1d2009.7581754898429!2d10'
                '.927372341251292!3d59.75346552497313!2m3!1f0!2f0!3f0!3m2'
                '!1i1024!2i768!4f13.1!3m3!1m2!1s0x46415df5da495a43'
                '%3A0xd9ab4ea8e930b13d!2sKarma+Shedrup+Ling+retreatsenter'
                '!5e0!3m2!1sen!2sus!4v1474500473508'
            ),
            address='Siggerudveien 734, 1400 Ski',
            tlf=None
        ),
        'Retreatsenter i Sørmarka.'
    ),
    (
        dict(
            code='NLT',
            slug='nlt',
            title='Nordlystempelet',
            # get from map embed URI
            map_query=(
                'pb=!1m18!1m12!1m3!1d310979.3974995069!2d15.250105274612977'
                '!3d68.35229158430016!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13'
                '.1!3m3!1m2!1s0x45dc3cb51265895f%3A0xa2c4ac9f784353c1!'
                '2sForrnesvegen%20116%2C%208412%20Vestbygd!5e0!3m2!'
                '1sno!2sno!4v1765309464222!5m2!1sno!2sno'
            ),
            address='Forrnesvegen 116, 8412 Vestbygd',
            tlf=None
        ),
        'Lavvo-tempel ved den øde Øksfjorden i Lødingen kommune.'
    ),
)


def publish_page(page, page_parent, default_body_string, user):
    '''
    Function for reliably creating an event_page, since django's
    update_or_create() doesn't handle Treebeard MP_node attributes.
    MP_node is used by Wagtail pages for tree structured hiearchy.
    '''

    logger.debug('publishing page: {}'.format(page))

    paragraph = '<p>{}</p>'.format(default_body_string)
    page.body = [
        ('paragraph', RichText(paragraph))
    ]
    page.live = True
    page.owner = user
    page.draft_title = None
    page.has_unpublished_changes = False

    with transaction.atomic():
        page_parent.add_child(instance=page)


def slugify(url):
    '''
    Helper function for converting Norwegian characters to ASCII representation.
    '''

    url = url.lower()

    for substitution in (('æ', 'ae'), ('ø', 'oe'), ('å', 'aa'),):
        url = url.replace(*substitution)

    return django_slugify(url)


def get_credentials():
    '''
    Gets credentials for server to server google API communications.
    '''

    json_path = os.environ.get('JWT_JSON_PATH')
    scopes = ('https://www.googleapis.com/auth/calendar.readonly',)

    credentials = None

    if json_path:
        credentials = Credentials.from_service_account_file(
            json_path,
            scopes=scopes,
        )
    else:
        private_key = os.environ['GCAL_PRIVATE_KEY'].replace('\\n', '\n')
        credentials = Credentials.from_service_account_info(
            {
                'type': 'service_account',
                'client_email': os.environ['GCAL_CLIENT_MAIL'],
                'private_key': private_key,
                'token_uri': 'https://accounts.google.com/o/oauth2/token',
            },
            scopes=scopes,
        )

    assert credentials is not None
    return credentials


def get_remote_calendars(service, items='id,summary,description,accessRole'):
    '''
    Fetches calendar list from Google Calendar API.
    '''

    return service.calendarList().list(
        fields=f'items({items})',
        minAccessRole='owner').execute().get('items', [])


def sync_event_instance_entry(gcal_event, event_page):
    '''
    Function for creating an event instance and couple with an EventPage.

    Returns the google calendar event object if the summary has changed.
    '''

    # TODO: is it necessary to handle cancelled instance?
    start, end, full_day = json_time_to_utc(gcal_event)

    instance_data = dict(
        start=start,
        end=end,
        full_day=full_day,
        centre=event_page.calendar.centre,
        event_page=event_page
    )

    event_instance_object, _ = Event.objects.update_or_create(
        event_id=gcal_event['id'],
        defaults=instance_data
    )

    event_instance_object.save()
    summary = get_valid_event_str_attr(gcal_event, 'summary')

    if summary != event_page.title:
        logger.info('Summary changed from %s to %s', event_page.title, summary)
        return gcal_event


def todays_iso_date():
    skewed_date = dt.date.today() - dt.timedelta(days=DEBUG_DATE_SKEW)
    return skewed_date.isoformat() + 'T00:00:00Z'


def request_events(service, calendar_id, page_token):
    '''
    Request object containing event list from Google calendar API.
    '''

    gcal_params = {
        'calendarId': calendar_id,
        'singleEvents': True,
        'timeMin': todays_iso_date()
    }

    if page_token is not None:
        gcal_params['pageToken'] = page_token

    logger.info('List events w/ params: {}'.format(gcal_params))

    response = service.events().list(**gcal_params).execute()

    logger.info(
        'Gcal returned {} items (page_token: {}, next_sync_token: {})'.format(
            len(response['items']),
            response.get('nextPageToken'),
            response.get('nextSyncToken'),
        )
    )

    return response


def create_db_calendars(service):
    '''
    Utility function for storing calendars from Google Calendar API to the
    local database.
    '''

    calendars = get_remote_calendars(service)
    pertinent_codes = {d['code'] for d, _ in CENTRES}

    for cal in calendars:
        # Assumes the pertinent calendar names are formed as:
        # "<Centre code> - Program"
        center_code = cal['summary'].split('-')[0].strip()
        if center_code not in pertinent_codes:
            continue

        fk = Centre.objects.get(code=center_code)
        Calendar(
            calendar_id=cal['id'],
            summary=cal['summary'],
            description=cal['description'],
            public=cal['summary'].endswith('program'),
            centre=fk
        ).save()

        logger.info('Created calendar for: "{}"'.format(center_code))


def ensure_center(centre_data, centre_parent_page, user):
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


def create_event_page(event_data, centre_page, user):
    '''
    Helper function for publishing a manually created Wagtail EventPage object.
    '''

    event_attributes, event_description = event_data
    master_event_id = event_attributes['master_event_id']
    event_page = EventPage(**event_attributes)
    publish_page(event_page, centre_page, event_description, user)

    logger.info(
        'Created event page for event %s (%s)',
        event_data[0]['title'], master_event_id
    )

    return event_page


def register_centers(user):
    '''
    Utility function for registering the defined CENTRES into the
    database.
    '''

    try:
        centre_parent_page = HomePage.objects.get(title='Sentre')
    except HomePage.DoesNotExist:
        centre_parent_page = HomePage(
            title='Sentre',
            slug='sentre',
            show_in_menus=True
        )
        site_root_page = Page.get_root_nodes()[0]
        main_page = site_root_page.get_children()[0]
        main_page.add_child(instance=centre_parent_page)

    for centre_data in CENTRES:
        ensure_center(centre_data, centre_parent_page, user)
        logger.info('registerred centre: "{}"'.format(centre_data[0]['title']))


def json_time_to_utc(gcal_event):
    '''
    Extracts a google calendar time range (start/stop) json object and returns
    a UTC datetime object and full-day boolean status.
    '''

    timerange = (gcal_event['start'], gcal_event['end'],)

    # TODO: verify that google calendar has sanity checked date/dateTime fields
    full_day = all(time.get('date') for time in timerange) and not (
        any(time.get('dateTime') for time in timerange))

    key = 'date' if full_day else 'dateTime'
    start, end = (
        dt.datetime.fromisoformat(time.get(key)).astimezone(dt.timezone.utc)
        for time in timerange
    )

    return start, end, full_day


def delete_cancelled_event_instance(event_instance):
    logger.debug(
        'Cancellation removed instance: "{}"'.format(event_instance)
    )

    event_instance.delete()


def delete_cancelled_event_page(event_page):
    logger.debug(
        'Cancellation removing page: "{}"'.format(event_page)
    )

    event_page.delete()


def handle_cancelled_multi_event(service, calendar, event):
    try:
        cancelled_event = Event.objects.get(event_id=event['id'])
    except Event.DoesNotExist:
        return

    event_page = cancelled_event.event_page

    cancelled_event.cancelled = True
    cancelled_event.save()

    cancelled_instances = event_page.event_instances.all()

    if any(not event.cancelled for event in cancelled_instances):
        return

    for event in cancelled_instances:
        delete_cancelled_event_instance(event)

    delete_cancelled_event_page(event_page)


def handle_cancellation(service, calendar, event):
    handling_singular_event = 'recurringEventId' not in event

    logger.info(
        'Handling cancelled {} event: {} ({})'.format(
            'singular' if handling_singular_event else 'multi',
            event.get('summary'),
            event['id']
        )
    )

    if handling_singular_event:
        try:
            cancelled_event = Event.objects.get(event_id=event['id'])
        except Event.DoesNotExist:
            return

        event_page = cancelled_event.event_page

        delete_cancelled_event_instance(cancelled_event)
        delete_cancelled_event_page(event_page)

    else:
        handle_cancelled_multi_event(service, calendar, event)


def get_valid_event_str_attr(event, attr_name):
    attr = event.get(attr_name)
    invalid_attr = (
        attr is None
        or attr == ''
        or all(c in string.whitespace for c in attr)
    )

    if invalid_attr:
        logger.error(f'Invalid calendar event ({event}) '
                     f'`{attr_name}` value: `{attr}`')
        return None
    else:
        return attr


def sync_event_page(calendar, user, master_gcal_event):
    logger.debug('syncing master_gcal_event: %s', master_gcal_event)

    title = get_valid_event_str_attr(master_gcal_event, 'summary')
    description = master_gcal_event.get('description', '')

    try:
        EventPage.objects.get(slug=slugify(title))
    except EventPage.DoesNotExist:
        slug = slugify(title)
    else:
        # TODO: Look into prompting user to stop duplicating events!
        logger.error(
            f'sync_event_page FAILED! Duplicate event Title/Summary: `{title}`'
        )
        slug = slugify('{}-{}'.format(title, str(uuid4())[:6]))

    event_page_data = (
        dict(
            title=title,
            slug=slug,
            master_event_id=master_gcal_event['id'],
            recurrence=master_gcal_event.get('recurrence'),
            google_cal_url=master_gcal_event['htmlLink'],
            creator=master_gcal_event.get('creator'),
            calendar=calendar
        ),
        description
    )

    event_parent_page = Centre.objects.get(code=calendar.centre.code)

    event_page = create_event_page(
        event_data=event_page_data,
        centre_page=event_parent_page,
        user=user
    )

    start, end, _ = json_time_to_utc(master_gcal_event)
    current_time = dt.datetime.now(dt.timezone.utc)

    if current_time - dt.timedelta(days=DEBUG_DATE_SKEW) < end:
        sync_event_instance_entry(master_gcal_event, event_page)

    logger.info(
        'sync_event_page created event page for single event: "{}" ({})'
        .format(master_gcal_event['id'], master_gcal_event.get('summary'))
    )

    return event_page


def get_synced_events(service, calendar, page_token, user, recurring_events):
    '''
    Create calendar events in the database.

    Collects events from Google Calendar using the 'singleEvents'
    parameters, which will expand all event instances into single events. Any
    recurring event will be collected in the `recurring_events` dictionary using
    the master event id (recurringEventId) as the key and a list of event ids as
    the value. The dictionary is used by sync_recurring_events().

    If an event does not contain a recurringEventId, it is a non-recurring event
    and the EventPage representing the event can be created immediately.

    A page_token is used to support pagination with Google Calendar, which will
    break up a huge response into smaller responses. The token will be `None`
    when the all the data has been transmitted.
    '''
    events_response = request_events(service, calendar.calendar_id, page_token)
    next_page_token = events_response.get('nextPageToken')

    for gcal_event in events_response['items']:
        if gcal_event.get('status') == 'cancelled':
            handle_cancellation(calendar, gcal_event)
            continue

        try:
            master_event_id = gcal_event['recurringEventId']
        except KeyError:
            sync_event_page(calendar, user, master_gcal_event=gcal_event)
            continue

        if master_event_id not in recurring_events:
            recurring_events[master_event_id] = []

        recurring_events[master_event_id].append(gcal_event)

        logger.info(
            'get_synced_events added recurrence {} to event: "{}" ({})'
            .format(
                gcal_event['id'],
                master_event_id,
                gcal_event.get('summary')
            )
        )

    return next_page_token, recurring_events


def sync_recurring_events(service, calendar, recurring_events, user):
    '''
    Iterates key-values in recurring_events dictionary. From the key, creating
    a Wagtail EventPage based on a Google Calendar get-event request. From the
    value, all recurring instances in the value list will also be created as
    Event entries in the database.
    '''

    logger.info('--- Syncing recurring events ---')

    for master_event_id, event_list in recurring_events.items():
        logger.info(f'master_event_id: {master_event_id}')
        logger.debug(
            'event_list: '
            f'{json.dumps(event_list, indent=2, ensure_ascii=False)}'
        )

        try:
            master_event = service.events().get(
                calendarId=calendar.calendar_id,
                eventId=master_event_id,
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                failed_event, *_ = event_list
                logger.error(
                    f'Master Event not found! ({master_event_id}) '
                    f'{failed_event["summary"]}. Skipping recurring event sync'
                )
                continue
            raise

        if master_event['status'] == 'cancelled':
            handle_cancellation(calendar, master_event)
            continue

        # Need to add the master event if it has come to pass, but if not it
        # will already be present in the event_list, and must be removed to
        # avoid duplicate event instances.
        master_event_time = json_time_to_utc(master_event)
        normalized_events = [
            e for e in event_list if json_time_to_utc(e) != master_event_time
        ]

        if len(normalized_events) == 0:
            warnings.warn(
                (
                    'Creating EventPage ({}) with ZERO events!!!'
                    .format(master_event)
                ),
                ResourceWarning
            )

        event_page = sync_event_page(
            calendar,
            user,
            master_gcal_event=master_event
        )

        if event_page is None:
            logger.error(
                'sync_event_page for recurring failed! '
                '(Calendar: {}, master event: {})'
                .format(calendar, master_event)
            )
            return

        logger.info(
            'Creating {} event instances for Page: {}'.format(
                len(normalized_events),
                event_page.title
            )
        )

        logger.debug(
            'event instances for Page {}: {}'.format(
                event_page.title,
                normalized_events
            )
        )

        changed = False

        for event_instance in normalized_events:
            changed = sync_event_instance_entry(event_instance, event_page)

        if changed:
            event_page.title = changed['summary']
            event_page.save()


def sync_db_calendar_events(service, user):
    '''
    Synchronize all public calendars in local database.
    '''

    should_exist = {centre['code'] for centre, _ in CENTRES}
    exists = {c.centre.code for c in Calendar.objects.all()}
    unregistered_centre = should_exist - exists != set()

    if unregistered_centre:
        register_centers(user)

    for calendar in Calendar.objects.filter(public=True):
        recurring_events = {}
        next_page_token = None

        while True:
            try:
                next_page_token, recurring_events = get_synced_events(
                    service,
                    calendar,
                    next_page_token,
                    user,
                    recurring_events
                )
            except HttpError as http_err:
                if http_err.resp.status != 410:
                    raise http_err

                logger.info(
                    'Sync token EXPIRED!\nRemoving sync token and event data ..'
                )
                # calendar.sync_token = None
                Event.objects.all().delete()

                # leave except block without breaking while loop
                next_page_token = None
                continue

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

    Event.objects.all().delete()
    EventPage.objects.all().delete()
    Calendar.objects.all().delete()

    user = get_user(user_name)

    service = discovery.build(
        "calendar",
        "v3",
        credentials=get_credentials(),
    )
    register_centers(user)
    create_db_calendars(service)
    sync_db_calendar_events(service, user)


def sync_events(user_name=None):
    '''
    For CRONjobs or from a google API signal.

    Will update the calendars incrementally using the syncToken.
    '''

    Event.objects.all().delete()
    EventPage.objects.all().delete()

    user = get_user(user_name)
    service = discovery.build(
        "calendar",
        "v3",
        credentials=get_credentials(),
    )
    sync_db_calendar_events(service, user)
