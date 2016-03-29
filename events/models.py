from django.db import models
from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class EventSignupPage(Page):
    # TODO: use on_delete=models.CASCADE, but respect Event's FK's on_delete
    event_calendar_entry = models.ForeignKey(
        'gcal.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='signup'
    )
    # TODO: normalize to uppercase
    course_code = models.CharField(blank=False, max_length=8)
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
    PAYMENT_CHOICES = (
        ('donation', 'Donasjon'),
        ('full', 'Èn pris for hele kurset'),
        ('choice', 'Pris per valgte kursdag'),
    )
    payment = models.CharField(
        blank=False,
        choices=PAYMENT_CHOICES,
        max_length=20
    )
    earlybird_deadline = models.DateField(blank=True)
    full_price = models.IntegerField(blank=False)
    daily_price = models.IntegerField(blank=False)

    content_panels = Page.content_panels + [
        FieldPanel('event_calendar_entry'),
        FieldPanel('intro', classname='full'),
        FieldPanel('thankyou_page_title'),
        FieldPanel('speaker'),
        FieldPanel('payment'),
        FieldPanel('earlybird_deadline'),
        FieldPanel('full_price'),
        FieldPanel('daily_price'),
    ]

    def serve(self, request):
        from events.forms import GenericPersonForm

        if request.method == 'POST':
            form = GenericPersonForm(request.POST)

            if form.is_valid():
                # TODO: paypal generation
                person = form.save()

                return render(
                    request,
                    'events/thankyou.html',
                    {
                        'page': self,
                        'person': person,
                    }
                )
        else:
            form = GenericPersonForm(dates=list(range(4)))

        return render(
            request,
            'events/signup_form.html',
            {
                'page': self,
                'form': form,
            }
        )


class Teacher(Page):
    name = models.CharField(blank=False, max_length=100)
    bio = RichTextField(blank=False)
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='+'
    )


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

    gender = models.CharField(blank=False, choices=GENDER_CHOICES, max_length=1)
    first_name = models.CharField(blank=False, max_length=40)
    sir_name = models.CharField(blank=False, max_length=120)
    email = models.EmailField(blank=False, max_length=120)
    # TODO: add validator
    phone_number = models.CharField(blank=False, max_length=20)
    payment = models.CharField(
        blank=False,
        choices=PAYMENT_CHOICES,
        max_length=20
    )
    # TODO: add description
    discount = models.BooleanField()
