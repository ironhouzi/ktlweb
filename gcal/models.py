from django.db import models


class Centre(models.Model):
    code = models.CharField(
        'Kode',
        max_length=3,
        primary_key=True
    )
    name = models.CharField('Navn', max_length=200, blank=False)
    address = models.TextField('Addresse', blank=False)
    description = models.CharField('Beskrivelse', max_length=200, blank=False)
    tlf = models.CharField(max_length=18, null=True, blank=True)
    image = models.ImageField('Bilde', null=True, blank=True)

    def __str__(self):
        return self.code


class Calendar(models.Model):
    calendar_id = models.CharField(max_length=200, primary_key=True)
    summary = models.CharField('Oppsummering', max_length=200)
    description = models.CharField('Beskrivelse', max_length=1000)
    public = models.BooleanField('Offentlig kalender', blank=False)
    sync_token = models.CharField(max_length=50, null=True, blank=True)
    centre = models.ForeignKey(
        Centre,
        on_delete=models.SET_NULL,
        verbose_name='Senter',
        related_name='centre',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.summary


class Event(models.Model):
    event_id = models.CharField(max_length=1024, primary_key=True)
    start = models.DateTimeField('Start', null=False, blank=False)
    end = models.DateTimeField('Slutt', null=False, blank=False)
    summary = models.CharField('Oppsummering', max_length=400)
    full_day = models.BooleanField('Full dag', blank=False)
    html_link = models.URLField('Google lenke', null=True, blank=True)
    # TODO: recurrence list, recurringEventId, description string,
    # creator
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.PROTECT,
        verbose_name='Kalender',
        related_name='calendar',
        null=False,
        blank=False
    )

    def __str__(self):
        return self.summary

