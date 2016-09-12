from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
# from wagtail.wagtailsearch import index

from home.models import AbstractHomePage


class Centre(AbstractHomePage):
    code = models.CharField(
        'Kode',
        max_length=3,
        blank=False
    )
    address = models.TextField('Addresse', blank=False)
    google_location = models.CharField(
        'Google-lokasjon',
        max_length=255,
        blank=False
    )
    tlf = models.CharField(
        'Telefonnummer',
        max_length=18,
        null=True,
        blank=True
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('code'),
        FieldPanel('address'),
        FieldPanel('tlf'),
        ImageChooserPanel('image'),
    ]


class Calendar(models.Model):
    calendar_id = models.CharField(max_length=200, primary_key=True)
    summary = models.CharField('Oppsummering', max_length=200)
    description = models.CharField('Beskrivelse', max_length=1000)
    public = models.BooleanField('Offentlig kalender', blank=False)
    sync_token = models.CharField(max_length=50, null=True, blank=True)
    centre = models.OneToOneField(
        'Centre',
        on_delete=models.SET_NULL,
        verbose_name='Senter',
        related_name='centre',
        null=True,
        blank=False
    )

    def __str__(self):
        return self.summary


class Event(models.Model):
    event_id = models.CharField(max_length=1024, primary_key=True)
    start = models.DateTimeField('Start')
    end = models.DateTimeField('Slutt')
    full_day = models.BooleanField('Full dag', default=False)
    url = models.URLField('Lenke')
    cancelled = models.BooleanField('Kansellert', default=False)
    event_page = models.ForeignKey(
        'EventPage',
        on_delete=models.SET_NULL,
        verbose_name='Aktivitetside',
        related_name='event_instances',
        null=True,
        blank=False
    )

    def __str__(self):
        return self.event_page.title


class EventPage(AbstractHomePage):
    master_event_id = models.CharField(max_length=1024, unique=True)
    creator = JSONField(null=True, blank=True)
    recurrence = ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True
    )
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.PROTECT,
        verbose_name='Kalender',
        related_name='events',
        null=True,
        blank=False
    )

    # TODO: create inline panel for recurrence
    content_panels = Page.content_panels + [
        FieldPanel('calendar'),
    ]

    def __str__(self):
        return '<EventPage: "{}" ({})>'.format(self.title, self.master_event_id)
