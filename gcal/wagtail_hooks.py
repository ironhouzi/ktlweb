from gcal import views

# from wagtail.contrib.modeladmin.helpers import ButtonHelper, PermissionHelper
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)

from django.urls import reverse

# from .models import Centre, Calendar, Event
from .models import Event


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
    menu_label = 'Kalender'
    menu_icon = 'date'
    menu_order = 200
    add_to_settings_menu = False
    list_display = (
        'event_name',
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


modeladmin_register(EventAdmin)
