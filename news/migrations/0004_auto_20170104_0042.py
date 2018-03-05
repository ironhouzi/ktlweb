# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 23:42
from __future__ import unicode_literals

from django.db import migrations
import home.models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20161226_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsentryindex',
            name='body',
            field=wagtail.core.fields.StreamField((('h2styled', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='stilisert overskrift')), ('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('sitat')), ('attribution', wagtail.core.blocks.CharBlock('tilegnelse'))), label='Sitat')), ('aligned_image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.core.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('markdown', home.models.MarkDownBlock(label='markdown')), ('news_feed', wagtail.core.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold'),
        ),
        migrations.AlterField(
            model_name='newsentryindex',
            name='sidepanel',
            field=wagtail.core.fields.StreamField((('eventviewer', wagtail.core.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?'))), label='Vis kommende aktiviteter')), ('linkviewer', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('link', wagtail.core.blocks.StructBlock((('external_url', wagtail.core.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.core.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.core.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Lenke- fremviser', template='home/blocks/sidepanel_links.html')), ('videoembed', wagtail.core.blocks.StructBlock((('caption', wagtail.core.blocks.TextBlock(label='Seksjonstittel', required=True)), ('video_id', wagtail.core.blocks.TextBlock(label='Youtube video-id', required=True))), label='Youtube- video'))), default='', verbose_name='sidepanel'),
        ),
    ]
