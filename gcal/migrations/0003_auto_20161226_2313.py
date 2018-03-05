# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 22:13
from __future__ import unicode_literals

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('gcal', '0002_auto_20161221_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centre',
            name='headingpanel',
            field=wagtail.core.fields.StreamField((('quicklinks', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('link', wagtail.core.blocks.StructBlock((('external_url', wagtail.core.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.core.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.core.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html')), ('bannerimage', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),), label='Bannerbilde.\nOBS: 2048x500 piksler!'))), default='', verbose_name='overpanel'),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='headingpanel',
            field=wagtail.core.fields.StreamField((('quicklinks', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('link', wagtail.core.blocks.StructBlock((('external_url', wagtail.core.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.core.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.core.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.core.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html')), ('bannerimage', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock(label='Bilde')),), label='Bannerbilde.\nOBS: 2048x500 piksler!'))), default='', verbose_name='overpanel'),
        ),
    ]
