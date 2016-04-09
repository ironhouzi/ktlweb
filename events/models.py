from django.db import models
from django.shortcuts import render
from django.contrib.postgres.fields import JSONField

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, InlinePanel, PageChooserPanel
)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey


class EventSignupPage(Page):
    # TODO: use on_delete=models.CASCADE, but respect Event's FK's on_delete
    calendar_entry = models.ForeignKey(
        'gcal.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='signup_page'
    )
    # TODO: normalize to uppercase
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255,
        help_text='Title text for "Thank you" page'
    )
    speaker = models.ForeignKey(
        'events.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    payment = models.BooleanField()
    earlybird_deadline = models.DateField(blank=True)

    content_panels = Page.content_panels + [
        PageChooserPanel('calendar_entry'),
        FieldPanel('intro', classname='full'),
        FieldPanel('thankyou_page_title'),
        PageChooserPanel('speaker'),
        FieldPanel('payment'),
        FieldPanel('earlybird_deadline'),
        InlinePanel('skus', label='Kursalternativer'),
    ]

    def serve(self, request):
        from events.forms import EventRegistration

        if request.method == 'POST':
            form = EventRegistration(request.POST)

            if form.is_valid():
                event_signup = form.save()

                return render(
                    request,
                    'events/thankyou.html',
                    {
                        'page': self,
                        'event_signup': event_signup,
                    }
                )
        else:
            form = EventRegistration(
                name=self.title,
                skus=self.skus,
                event_begin=self.calendar_entry.start,
                event_end=self.calendar_entry.end
            )

        return render(
            request,
            'events/signup_form.html',
            {
                'page': self,
                'form': form,
            }
        )


class EventSKU(Orderable):
    event = ParentalKey(EventSignupPage, related_name='skus')
    course_code = models.CharField(blank=False, max_length=8)
    name = models.CharField(blank=False, max_length=100)
    price = models.IntegerField(blank=False)
    first_day = models.DateField(blank=True, null=True)
    last_day = models.DateField(blank=True, null=True)
    multi_itemed = models.BooleanField()
    flat_rate_day = models.BooleanField()

    panels = [
        FieldPanel('course_code'),
        FieldPanel('name'),
        FieldPanel('price'),
        FieldPanel('first_day'),
        FieldPanel('last_day'),
        FieldPanel('multi_itemed'),
        FieldPanel('flat_rate_day'),
    ]


class Teacher(Page):
    bio = RichTextField(blank=False)
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        ImageChooserPanel('image'),
    ]


# TODO: use RegexValidator!
def phonenumber_validator(value):
    pass


class EventSignupEntry(models.Model):
    GENDER_CHOICES = (('f', 'female'), ('m', 'male'),)
    PAYMENT_CHOICES = (
        ('online', 'Pay online'),
        ('invoice', 'Receive invoice via email'),
        ('later', 'Pay later without receiving invoice'),
    )

    gender = models.CharField(
        blank=False,
        choices=GENDER_CHOICES,
        default='f',
        max_length=1
    )
    first_name = models.CharField(blank=False, max_length=40)
    sir_name = models.CharField(blank=False, max_length=120)
    email = models.EmailField(blank=False, max_length=120)
    # TODO: add validator
    phone_number = models.CharField(blank=False, max_length=20)
    payment = models.CharField(
        blank=False,
        choices=PAYMENT_CHOICES,
        default='online',
        max_length=20
    )
    # TODO: add description
    discount = models.BooleanField()
    # TODO: add datefield validators based on event time range
    arrival = models.DateField(blank=False)
    departure = models.DateField(blank=False)
    paypal_transactions = JSONField()
