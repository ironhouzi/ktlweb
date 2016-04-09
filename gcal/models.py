from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from home.models import HomePageStreamBlock


class Centre(Page):
    code = models.CharField(
        'Kode',
        max_length=3,
        blank=False
    )
    address = models.TextField('Addresse', blank=False)
    description = models.CharField('Beskrivelse', blank=False, max_length=200)
    information = StreamField(HomePageStreamBlock(), verbose_name='information', null=True)
    tlf = models.CharField(max_length=18, null=True, blank=True)
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
        FieldPanel('description'),
        StreamFieldPanel('information'),
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
        Centre,
        on_delete=models.SET_NULL,
        verbose_name='Senter',
        related_name='centre',
        null=True,
        blank=False
    )

    def __str__(self):
        return self.summary


class Event(Page):
    event_id = models.CharField(max_length=1024)
    start = models.DateTimeField('Start', null=False, blank=False)
    end = models.DateTimeField('Slutt', null=False, blank=False)
    full_day = models.BooleanField('Full dag', blank=False)
    recurrence = ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True
    )
    recurring_event_id = models.CharField(
        max_length=1024,
        null=True,
        blank=True
    )
    description = models.TextField(null=True, blank=False)
    creator = JSONField(null=True, blank=True)
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.PROTECT,
        verbose_name='Kalender',
        related_name='events',
        null=True,
        blank=False
    )

    content_panels = Page.content_panels + [
        FieldPanel('start'),
        FieldPanel('end'),
        FieldPanel('description'),
        FieldPanel('calendar'),
    ]
