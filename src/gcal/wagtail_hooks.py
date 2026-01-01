import logging

from gcal import views

from django.core.exceptions import PermissionDenied
from django.urls import reverse, path

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.tables import Column
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import (
    CreateView,
    DeleteView,
    EditView,
    SnippetViewSet,
    SnippetViewSetGroup,
)

from .models import Event, Centre


class ForbiddenView:
    def dispatch(self, request, *args, **kwargs):
        raise PermissionDenied('Action is prohibited!')


class NoCreateEventView(ForbiddenView, CreateView):
    pass


class NoEditEventView(ForbiddenView, EditView):
    pass


class NoDeleteEventView(ForbiddenView, DeleteView):
    pass


class EventNameColumn(Column):
    def __init__(self, name='hendelsesnavn', label='Navn', **kwargs):
        super().__init__(name, label=label, **kwargs)

    def get_value(self, obj):
        return obj.event_page.title


class EventCreatorColumn(Column):
    def __init__(self, name='hendelsesoppretter', label='Registrator', **kwargs):
        super().__init__(name, label=label, **kwargs)

    def get_value(self, obj):
        email = obj.event_page.creator.get('email', 'ukjent')
        return obj.event_page.creator.get('displayName', email)


class EventAdmin(SnippetViewSet):
    model = Event
    menu_label = 'Aktiviteter'
    menu_icon = 'date'
    add_to_settings_menu = False
    list_display = (
        EventNameColumn(),
        EventCreatorColumn(),
        'centre',
        'start',
        'end',
        'full_day',
        'event_id',
    )

    list_filter = ('start', 'full_day')
    search_fields = ('start', 'end', 'full_day')
    copy_view_enabled = False

    add_view_class = NoCreateEventView
    edit_view_class = NoEditEventView
    delete_view_class = NoDeleteEventView


class ModeratorMenuItem(MenuItem):
    def is_shown(self, request):
        return (
            request.user.is_authenticated and (
                request.user.is_superuser
                or request.user.groups.filter(name='Moderators').exists()
            )
        )


@hooks.register('register_admin_menu_item')
def register_event_sync():
    return ModeratorMenuItem(
        'Oppdater kalender',
        reverse(views.sync_google_calendar),
        order=300,
        icon_name='date'
    )


class KalenderGroupAdmin(SnippetViewSetGroup):
    menu_label = 'Kalender'
    menu_icon = 'date'
    menu_order = 200
    items = (EventAdmin,)


register_snippet(EventAdmin)
