from gcal import views

# from wagtail.contrib.modeladmin.helpers import ButtonHelper, PermissionHelper
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)

from django.urls import reverse

# from .models import Centre, Calendar, Event
from .models import Event, Centre


class ModifiedButtons(ButtonHelper):
    '''
    Removes buttons: 'modify' and 'delete', and changes the 'create' button
    action to syncronize Events/EventPages with Google Calendar.
    '''

    def add_button(self, classnames_add=[], classnames_exclude=[]):
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)

        return {
            'url': reverse(views.sync_google_calendar),
            'label': 'Synkronisér',
            'classname': cn,
            'title': 'Synkronisér Google Kalendere'
        }

    def get_buttons_for_obj(self, obj, exclude=[], classnames_add=[],
                            classnames_exclude=[]):
        return []


class EventAdmin(ModelAdmin):
    model = Event
    menu_label = 'Aktiviteter'
    menu_icon = 'date'
    add_to_settings_menu = False
    list_display = (
        'event_name',
        'creator',
        'centre',
        'start',
        'end',
        'full_day',
        'event_id',
    )
    list_filter = ('start', 'full_day')
    search_fields = ('start', 'end', 'full_day')
    button_helper_class = ModifiedButtons

    def event_name(self, obj):
        return obj.event_page.title

    def creator(self, obj):
        email = obj.event_page.creator.get('email', 'ukjent')
        return obj.event_page.creator.get('displayName', email)


class CentreAdmin(ModelAdmin):
    model = Centre
    menu_label = 'Sentre'
    menu_icon = 'home'
    add_to_settings_menu = False


class KalenderGroupAdmin(ModelAdminGroup):
    menu_label = 'Kalender'
    menu_icon = 'date'
    menu_order = 200
    items = (EventAdmin, CentreAdmin)


modeladmin_register(KalenderGroupAdmin)
