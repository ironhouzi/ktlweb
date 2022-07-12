import httplib2
import os
import arrow
import json
import logging
import datetime
import warnings

from uuid import uuid4

from pytz import timezone

from apiclient import discovery
from apiclient.errors import HttpError
from oauth2client.client import SignedJwtAssertionCredentials


from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.text import slugify as django_slugify
from django.utils.timezone import (
    get_default_timezone_name, utc, localtime, make_aware, is_naive, now
)

from wagtail.core.models import Page
from wagtail.core.rich_text import RichText

from .models import Calendar, Centre, Event, EventPage
from home.models import HomePage

logger = logging.getLogger(__name__)

SCOPES = os.environ.get(
    'GCAL_SCOPES',
    'https://www.googleapis.com/auth/calendar.readonly'
)

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
    )
)


def publish_page(page, page_parent, default_body_string, user):
    '''
    Helper function for publishing a manually created Wagtail Page object.
    '''

    logger.debug('publishing page: {}'.format(page))

    paragraph = '<p>{}</p>'.format(default_body_string)
    page.body = [
        ('paragraph', RichText(paragraph))
    ]

    # only set page parent if handling newly created page
    # if page_parent is not None:
    if page.get_parent() is None:
        logger.debug('Set parent: {} for {}'.format(page_parent, page))

        try:
            page_parent.add_child(instance=page)
        except ValidationError:
            slug_string = '{}-{}'.format(page.slug, page.id)
            page.slug = slugify(slug_string)
            logger.debug('page slug set to: {}'.format(page.slug))
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
    summary = gcal_event.get('summary', 'Navnløs')

    if summary != event_page.title:
        logger.info('Summary changed from %s to %s', event_page.title, summary)
        return gcal_event


def poll_event_instances(service, calendar, page_token):
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

    logger.info('List events w/ params: {}'.format(gcal_params))

    response = service.events().list(**gcal_params).execute()

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

    logger.info(
        'Gcal returned {} items (page_token: {}, next_sync_token: {})'.format(
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


def update_or_create_event_page(event_data, centre_page, user):
    '''
    Function for reliably updating/creating an event_page, since django's
    update_or_create() doesn't handle Treebeard MP_node attributes.
    MP_node is used by Wagtail pages for tree structured hiearchy.
    '''

    event_data_attributes, event_description = event_data
    master_event_id = event_data_attributes['master_event_id']

    try:
        event_page = EventPage.objects.get(master_event_id=master_event_id)

        # Cannot use update_or_create, since treebeard attributes must be set in
        # publish_page prior to saving.
        for key, value in event_data_attributes.items():
            setattr(event_page, key, value)

        event_page.save()
        action = 'Updated'
    except EventPage.DoesNotExist:
        event_page = EventPage(**event_data_attributes)
        action = 'Created'

    publish_page(event_page, centre_page, event_description, user)

    logger.info(
        '%s event page for event %s (%s)',
        action, event_data[0]['title'], master_event_id
    )

    return event_page


def register_centers(user):
    '''
    Utility function for registering the three available centres into the
    database.
    '''

    centre_parent_page = None

    try:
        centre_parent_page = HomePage.objects.get(title='sentre')
    except HomePage.DoesNotExist:
        centre_parent_page = HomePage(
            title='sentre',
            slug='sentre',
            show_in_menus=True
        )
        site_root_page = Page.get_root_nodes()[0]
        main_page = site_root_page.get_children()[0]
        main_page.add_child(instance=centre_parent_page)

    for centre_data in CENTRES:
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


def get_event_parent_page(calendar, user):
    try:
        event_parent_page = Centre.objects.get(code=calendar.centre.code)
    except Centre.DoesNotExist:
        register_centers(user)
        event_parent_page = Centre.objects.get(code=calendar.centre.code)

    return event_parent_page


def sync_event_page(calendar, user, master_gcal_event):
    logger.debug('syncing master_gcal_event: %s', master_gcal_event)

    title = master_gcal_event.get('summary', 'Navnløs')

    try:
        EventPage.objects.get(slug=slugify(title))
        slug = slugify('{}-{}'.format(title, str(uuid4())[:6]))
    except EventPage.DoesNotExist:
        slug = slugify(title)

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
        master_gcal_event.get('description', 'Ingen beskrivelse')
    )

    event_parent_page = get_event_parent_page(calendar, user)

    event_page = update_or_create_event_page(
        event_data=event_page_data,
        centre_page=event_parent_page,
        user=user
    )

    start, end, _ = json_time_to_utc(master_gcal_event)
    current_time = now()

    if current_time < end:
        sync_event_instance_entry(master_gcal_event, event_page)

    logger.info(
        'handle_events created event page for single event: "{}" ({})'
        .format(master_gcal_event['id'], master_gcal_event.get('summary'))
    )

    return event_page


def handle_events(service, calendar, page_token, user, recurring_events):
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

    events_response = poll_event_instances(service, calendar, page_token)
    next_page_token = events_response.get('nextPageToken')
    # sync_token = events_response.get('nextSyncToken')

    # # Only the last paginated response contains a nextSyncToken
    # if next_page_token is None and sync_token is not None:
    #     calendar.sync_token = sync_token
    #     calendar.save()

    #     logger.info(
    #         'Saved into calendar "{}", sync token: "{}"'
    #         .format(calendar.centre.code, calendar.sync_token)
    #     )

    for gcal_event in events_response['items']:
        if gcal_event.get('status') == 'cancelled':
            handle_cancellation(service, calendar, gcal_event)
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
            'handle_events added recurrence {} to event: "{}" ({})'
            .format(
                gcal_event['id'],
                master_event_id,
                gcal_event.get('summary')
            )
        )

    return next_page_token, recurring_events


def reset_gcal_summary(service, calendar, event_page, summary_changed):
    '''
    Since the database model does not support individual summaries for
    event instances, the summaries are reset if a summary in the
    calendar backend has changed.
    '''

    # TODO: warn committer via email
    for event_instance in summary_changed:
        logger.debug('resetting %s', event_instance)
        event_instance['summary'] = event_page.title

        service.events().update(
            calendarId=calendar.calendar_id,
            eventId=event_instance['id'],
            body=event_instance['description'],
            sendNotifications=True
        ).execute()

        logger.info(
            'Reset modified title (event_id: {})'.format(event_instance)
        )


def error_mail(calendar, failed_event):
    mailto = failed_event['creator']['email']
    mail_from = 'webmaster@ktl.no'
    send_mail(
        'Unexpected error in Google Calendar event for ktl.no',
        (
            'Unfortunately, an error in Google Calendar has prohibited '
            'ktl.no to store the event:\n\n'
            f'{failed_event["summary"]} in calendar: {calendar}\n\n'
            'To rectify the problem, please remove the event from Google '
            'Calendar and recreate the event and synchronize at ktl.no\n\n'
            'If you have any questions, please send a mail to:\n'
            'webmaster@ktl.no.\n\n'
            'Sorry for the inconvenience and have a nice day.'
        ),
        mail_from,
        [mailto, mail_from],
        fail_silently=False
    )


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
                error_mail(calendar, failed_event)
                continue
            raise

        if master_event['status'] == 'cancelled':
            handle_cancellation(service, calendar, master_event)
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
            # reset_gcal_summary(service, calendar, event_page, summary_changed)


def sync_db_calendar_events(service, user):
    '''
    Synchronize all public calendars in local database.
    '''

    for calendar in Calendar.objects.filter(public=True):
        recurring_events = {}
        next_page_token = None

        while True:
            try:
                next_page_token, recurring_events = handle_events(
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

    service = get_calendar_service()
    register_centers(user)
    create_db_calendars(service)
    sync_db_calendar_events(service, user)


def sync_events(user_name=None):
    '''
    For CRONjobs or from a google API signal.

    Will update the calendars incrementally using the syncToken.
    '''

    Event.objects.all().delete()

    user = get_user(user_name)
    service = get_calendar_service()
    sync_db_calendar_events(service, user)
    EventPage.objects.filter(event_instances=None).all().delete()
