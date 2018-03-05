from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
# from wagtail.search import index

from home.models import AbstractHomePage


class Centre(AbstractHomePage):
    code = models.CharField('Kode', max_length=3)
    address = models.TextField('Addresse', blank=False)
    google_location = models.CharField(
        'Google-lokasjon',
        max_length=255,
        blank=False
    )
    map_query = models.CharField(
        'GoogleMaps-lokasjon',
        max_length=1024,
        default=''
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

    def split_address(self):
        return self.address.split(',')

    class Meta:
        verbose_name = 'Senter'
        verbose_name_plural = 'Sentre'

    def __repr__(self):
        return '<Centre: "{}">'.format(self.code)

    def __str__(self):
        return self.code


class Calendar(models.Model):
    calendar_id = models.CharField(max_length=200, default='')
    summary = models.CharField('Oppsummering', max_length=200, default='')
    description = models.CharField('Beskrivelse', max_length=1000, default='')
    public = models.BooleanField('Offentlig kalender', blank=False)
    sync_token = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    centre = models.OneToOneField(
        'Centre',
        on_delete=models.SET_NULL,
        verbose_name='Senter',
        related_name='calendar',
        null=True,
        blank=False
    )

    def __str__(self):
        return self.summary


class Event(models.Model):
    event_id = models.CharField(max_length=1024)
    start = models.DateTimeField('Start')
    end = models.DateTimeField('Slutt')
    full_day = models.BooleanField('Full dag', default=False)
    cancelled = models.BooleanField('Kansellert', default=False)
    centre = models.ForeignKey(
        'Centre',
        on_delete=models.SET_NULL,
        verbose_name='Senter',
        related_name='events',
        null=True,
        blank=False
    )
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

    class Meta:
        ordering = ['start']
        verbose_name = 'Aktivitet'
        verbose_name_plural = 'Aktiviteter'


class EventPage(AbstractHomePage):
    master_event_id = models.CharField(max_length=1024, unique=True)
    creator = JSONField(null=True, blank=True)
    recurrence = ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True
    )
    google_cal_url = models.URLField('Google calendar lenke', max_length=1024)
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

    def __repr__(self):
        return '<EventPage: "{}" ({})>'.format(self.title, self.master_event_id)

    def __str__(self):
        if self.event_instances.count() == 0:
            return self.title
        else:
            return '{} ({}) | Starter: {} | Antall: {}'.format(
                self.title,
                self.calendar.centre,
                self.event_instances.first().start.strftime('%d. %b %Y'),
                self.event_instances.count()
            )

    class Meta:
        verbose_name = 'Aktivitetside'
        verbose_name_plural = 'Aktivitetsider'
