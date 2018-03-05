# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 14:51
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import home.models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('wagtailimages', '0015_fill_filter_spec_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar_id', models.CharField(default='', max_length=200)),
                ('summary', models.CharField(default='', max_length=200, verbose_name='Oppsummering')),
                ('description', models.CharField(default='', max_length=1000, verbose_name='Beskrivelse')),
                ('public', models.BooleanField(verbose_name='Offentlig kalender')),
                ('sync_token', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Centre',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('sitat')), ('attribution', wagtail.core.blocks.CharBlock('tilegnelse'))), label='Sitat')), ('aligned_image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.core.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('news_feed', wagtail.core.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold')),
                ('headingpanel', wagtail.core.fields.StreamField((('quicklinks', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('link', wagtail.core.blocks.StructBlock((('external_url', wagtail.core.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.core.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.core.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html'))), default='', verbose_name='overpanel')),
                ('sidepanel', wagtail.core.fields.StreamField((('eventviewer', wagtail.core.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?'))), label='Vis kommende aktiviteter')),), default='', verbose_name='sidepanel')),
                ('code', models.CharField(max_length=3, verbose_name='Kode')),
                ('address', models.TextField(verbose_name='Addresse')),
                ('google_location', models.CharField(max_length=255, verbose_name='Google-lokasjon')),
                ('map_query', models.CharField(default='', max_length=1024, verbose_name='GoogleMaps-lokasjon')),
                ('tlf', models.CharField(blank=True, max_length=18, null=True, verbose_name='Telefonnummer')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'verbose_name_plural': 'Sentre',
                'verbose_name': 'Senter',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=1024)),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('end', models.DateTimeField(verbose_name='Slutt')),
                ('full_day', models.BooleanField(default=False, verbose_name='Full dag')),
                ('cancelled', models.BooleanField(default=False, verbose_name='Kansellert')),
                ('centre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='gcal.Centre', verbose_name='Senter')),
            ],
            options={
                'verbose_name_plural': 'Aktiviteter',
                'verbose_name': 'Aktivitet',
                'ordering': ['start'],
            },
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('sitat')), ('attribution', wagtail.core.blocks.CharBlock('tilegnelse'))), label='Sitat')), ('aligned_image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.core.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('news_feed', wagtail.core.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold')),
                ('headingpanel', wagtail.core.fields.StreamField((('quicklinks', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('link', wagtail.core.blocks.StructBlock((('external_url', wagtail.core.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.core.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.core.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html'))), default='', verbose_name='overpanel')),
                ('sidepanel', wagtail.core.fields.StreamField((('eventviewer', wagtail.core.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?'))), label='Vis kommende aktiviteter')),), default='', verbose_name='sidepanel')),
                ('master_event_id', models.CharField(max_length=1024, unique=True)),
                ('creator', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('recurrence', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('google_cal_url', models.URLField(max_length=1024, verbose_name='Google calendar lenke')),
                ('calendar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='gcal.Calendar', verbose_name='Kalender')),
            ],
            options={
                'verbose_name_plural': 'Aktivitetsider',
                'verbose_name': 'Aktivitetside',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AddField(
            model_name='event',
            name='event_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_instances', to='gcal.EventPage', verbose_name='Aktivitetside'),
        ),
        migrations.AddField(
            model_name='calendar',
            name='centre',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar', to='gcal.Centre', verbose_name='Senter'),
        ),
    ]
