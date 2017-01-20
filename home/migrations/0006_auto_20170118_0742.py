# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-18 06:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import home.models
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('wagtailimages', '0016_deprecate_rendition_filter_relation'),
        ('home', '0005_auto_20170104_0042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField((('h2styled', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='stilisert overskrift')), ('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('hr', wagtail.wagtailcore.blocks.StructBlock(())), ('intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock(label='Sitat')), ('attribution', wagtail.wagtailcore.blocks.CharBlock(label='Tilegnelse', required=False))), label='Sitat')), ('aligned_image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.wagtailcore.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('markdown', home.models.MarkDownBlock(label='markdown')), ('news_feed', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold')),
                ('headingpanel', wagtail.wagtailcore.fields.StreamField((('quicklinks', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html')), ('bannerimage', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),), label='Bannerbilde.\nOBS: 2048x500 piksler!'))), default='', verbose_name='overpanel')),
                ('sidepanel', wagtail.wagtailcore.fields.StreamField((('eventviewer', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?'))), label='Vis kommende aktiviteter')), ('linkviewer', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Lenke- fremviser', template='home/blocks/sidepanel_links.html')), ('videoembed', wagtail.wagtailcore.blocks.StructBlock((('caption', wagtail.wagtailcore.blocks.TextBlock(label='Seksjonstittel', required=True)), ('video_id', wagtail.wagtailcore.blocks.TextBlock(label='Youtube video-id', required=True))), label='Youtube- video'))), default='', verbose_name='sidepanel')),
                ('intro', models.TextField(help_text='Kortfattet introduksjon, maks 4 linjer!', null=True, verbose_name='Ingress')),
                ('image', models.ForeignKey(help_text='Bildet må være minst 1200x400 piksler og ha formatet 3x1.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Bilde (1200x400)')),
            ],
            options={
                'verbose_name': 'Artikkel',
                'verbose_name_plural': 'Artikler',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ArticleIndex',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField((('h2styled', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='stilisert overskrift')), ('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('hr', wagtail.wagtailcore.blocks.StructBlock(())), ('intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock(label='Sitat')), ('attribution', wagtail.wagtailcore.blocks.CharBlock(label='Tilegnelse', required=False))), label='Sitat')), ('aligned_image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.wagtailcore.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('markdown', home.models.MarkDownBlock(label='markdown')), ('news_feed', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold')),
                ('headingpanel', wagtail.wagtailcore.fields.StreamField((('quicklinks', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Snarveis- panel', template='home/blocks/quicklink_list.html')), ('imageslider', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),)), icon='image', label='Bilde- karusell', template='home/blocks/imageslider_list.html')), ('bannerimage', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')),), label='Bannerbilde.\nOBS: 2048x500 piksler!'))), default='', verbose_name='overpanel')),
                ('sidepanel', wagtail.wagtailcore.fields.StreamField((('eventviewer', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')), ('centre_code', home.models.UpcomingEventCentreChoiceField(label='Hvilket senter?'))), label='Vis kommende aktiviteter')), ('linkviewer', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock((('link', wagtail.wagtailcore.blocks.StructBlock((('external_url', wagtail.wagtailcore.blocks.URLBlock(label='Ekstern lenke', required=False)), ('page_link', wagtail.wagtailcore.blocks.PageChooserBlock(label='Intern lenke', required=False)), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(label='Dokument- lenke', required=False))), label='lenke', required=True)), ('caption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Overskrift', max_length=50)), ('subcaption', wagtail.wagtailcore.blocks.CharBlock(help_text='Vær kortfattet, slik at teksten vises riktig.', label='Undertittel', max_length=50)), ('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/', label='Ikon', max_length=50)))), icon='link', label='Lenke- fremviser', template='home/blocks/sidepanel_links.html')), ('videoembed', wagtail.wagtailcore.blocks.StructBlock((('caption', wagtail.wagtailcore.blocks.TextBlock(label='Seksjonstittel', required=True)), ('video_id', wagtail.wagtailcore.blocks.TextBlock(label='Youtube video-id', required=True))), label='Youtube- video'))), default='', verbose_name='sidepanel')),
                ('image', models.ForeignKey(blank=True, help_text='Bildet må være minst 1200x400 piksler og ha formatet 3x1.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Bilde (1200x400)')),
            ],
            options={
                'verbose_name': 'Artikkelindeks',
                'verbose_name_plural': 'Artikkelindekser',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2styled', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='stilisert overskrift')), ('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift stor')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift mindre')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title', label='overskrift minst')), ('hr', wagtail.wagtailcore.blocks.StructBlock(())), ('intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='introduksjon')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow', label='paragraf')), ('pullquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock(label='Sitat')), ('attribution', wagtail.wagtailcore.blocks.CharBlock(label='Tilegnelse', required=False))), label='Sitat')), ('aligned_image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock(label='Bilde')), ('caption', wagtail.wagtailcore.blocks.RichTextBlock(label='Bildetekst')), ('alignment', home.models.ImageFormatChoiceBlock(label='Justering'))), icon='image', label='Justert bilde')), ('document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse', label='dokument')), ('markdown', home.models.MarkDownBlock(label='markdown')), ('news_feed', wagtail.wagtailcore.blocks.StructBlock((('count', home.models.NewsFeedCountChoiceField(label='Antall nyheter i visning')),), icon='grip', label='Siste nyheter'))), default='', verbose_name='hovedinnhold'),
        ),
    ]