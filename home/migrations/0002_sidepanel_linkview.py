# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-22 08:57
from __future__ import unicode_literals

from django.db import migrations
import home.models
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='sidepanel',
            field=wagtail.wagtailcore.fields.StreamField((('eventviewer', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')),), label='Vis kommende aktiviteter')), ('linkviewer', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Lenke- fremviser', template='home/blocks/sidepanel_links.html'))), verbose_name='sidepanel'),
        ),
    ]
