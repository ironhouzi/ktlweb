# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-04 12:37
from __future__ import unicode_literals

from django.db import migrations
import home.models
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_auto_20170129_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsentryindex',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2styled', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='stilisert overskrift')), ('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('hr', wagtail.wagtailcore.blocks.StructBlock(())), ('intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.RichTextBlock(label='Sitat')), ('attribution', wagtail.wagtailcore.blocks.CharBlock(label='Tilegnelse', required=False))), label='Sitat')), ('aligned_image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.wagtailcore.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('markdown', home.models.MarkDownBlock(label='markdown')), ('news_feed', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), blank=True, default='', verbose_name='hovedinnhold'),
        ),
        migrations.AlterField(
            model_name='newsentryindex',
            name='headingpanel',
            field=wagtail.wagtailcore.fields.StreamField((('quicklinks', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html')), ('bannerimage', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),), label='Bannerbilde.\nOBS: 2048x500 piksler!'))), blank=True, default='', verbose_name='overpanel'),
        ),
        migrations.AlterField(
            model_name='newsentryindex',
            name='sidepanel',
            field=wagtail.wagtailcore.fields.StreamField((('eventviewer', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?')), ('display_all', wagtail.wagtailcore.blocks.BooleanBlock(label='Langtidsvisning', required=False))), label='Vis kommende aktiviteter')), ('linkviewer', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Lenke- fremviser', template='home/blocks/sidepanel_links.html')), ('videoembed', wagtail.wagtailcore.blocks.StructBlock((('caption', wagtail.wagtailcore.blocks.TextBlock(label='Seksjonstittel', required=True)), ('video_id', wagtail.wagtailcore.blocks.TextBlock(label='Youtube video-id', required=True))), label='Youtube- video'))), blank=True, default='', verbose_name='sidepanel'),
        ),
    ]
