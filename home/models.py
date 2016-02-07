from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailcore.blocks import (
    TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, ListBlock,
    URLBlock, PageChooserBlock
)
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, StreamFieldPanel, TabbedInterface, ObjectList
)
from wagtail.wagtailsearch import index


class PullQuoteBlock(StructBlock):
    quote = TextBlock('sitat')
    attribution = CharBlock('tilegnelse')

    def __str__(self):
        return 'sitat'

    class Meta:
        icon = 'openquote'


class UpcomingEventCountChoiceField(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ('3', 'Tre aktviteter'),
            ('5', 'Fem aktviteter'),
            ('7', 'Syv aktviteter'),
            ('10', 'Ti aktviteter'),
        )
    )


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ('left', 'Venstrejustér'),
            ('right', 'Høyrejustér'),
            # ('mid', 'Midtstill'),
            ('full', 'Full størrelse'),
        )
    )


class EventsBlock(StructBlock):
    count = UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')

    class Meta:
        icon = 'date'
        template='gcal/blocks/display_events.html'
        help_text = (
            'Ved å aktivere dette valget vil kommende aktiviteter vises.'
        )


class LinkBlock(StructBlock):
    external_url = URLBlock(label='Ekstern lenke', required=False)
    page_link = PageChooserBlock(label='Intern lenke', required=False)
    document = DocumentChooserBlock(label='Dokument- lenke', required=False)

    class Meta:
        abstract = True
        help_text = 'Velg kun èn lenke-type (ekstern/intern/dokument).'


class QuickLinkBlock(StructBlock):
    link = LinkBlock(label='lenke', required=True)
    caption = CharBlock(
        label='Overskrift',
        help_text='Vær kortfattet, slik at teksten vises riktig.',
        max_length=50
    )
    subcaption = CharBlock(
        label='Undertittel',
        help_text='Vær kortfattet, slik at teksten vises riktig.',
        max_length=50
    )
    icon = CharBlock(
        label='Ikon',
        help_text='Velg ikonnavn fra http://fontawesome.io/cheatsheet/',
        max_length=50
    )

    def get_context(self, value):
        context = super().get_context(value)
        link = value['link']

        if link['external_url']:
            value['url'] = link['external_url']
        elif link['page_link']:
            value['url'] = link['page_link'].url
        elif link['document']:
            value['url'] = link['document'].url
        else:
            value['url'] = '#'

        return context

    class Meta:
        icon = 'link'
        template='home/blocks/quicklink.html'


class ImageSliderBlock(StructBlock):
    image = ImageChooserBlock(label='Bilde')

    class Meta:
        icon = 'image'
        template='home/blocks/slider_image.html'


class ImageBlock(StructBlock):
    image = ImageChooserBlock(label='Bilde')
    caption = RichTextBlock(label='Bildetekst')
    alignment = ImageFormatChoiceBlock(label='Justering')


class HomePageStreamBlock(StreamBlock):
    h2 = CharBlock(label='overskrift stor', icon='title', classname='title')
    h3 = CharBlock(label='overskrift mindre', icon='title', classname='title')
    h4 = CharBlock(label='overskrift minst', icon='title', classname='title')
    intro = RichTextBlock(label='introduksjon', icon='pilcrow')
    paragraph = RichTextBlock(label='paragraf', icon='pilcrow')
    pullquote = PullQuoteBlock(label='Sitat')
    aligned_image = ImageBlock(label='Justert bilde', icon='image')
    document = DocumentChooserBlock(label='dokument', icon='doc-full-inverse')


class SidePanelStreamBlock(StreamBlock):
    eventviewer = EventsBlock(label='Vis kommende aktiviteter')


class HeadingPanelStreamBlock(StreamBlock):
    quicklinks = ListBlock(
        QuickLinkBlock(),
        icon='link',
        label='Snarveis- panel',
        template='home/blocks/quicklink_list.html'
    )
    imageslider = ListBlock(
        ImageSliderBlock(),
        icon='image',
        label='Bilde- karusell',
        template='home/blocks/imageslider_list.html'
    )


class HomePage(Page):
    body = StreamField(HomePageStreamBlock(), verbose_name='hovedinnhold')
    headingpanel = StreamField(
        HeadingPanelStreamBlock(),
        verbose_name='overpanel'
    )
    sidepanel = StreamField(SidePanelStreamBlock(), verbose_name='sidepanel')

    class Meta:
        verbose_name = "hjemmeside"

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    content_panels = [
        FieldPanel('title'),
        StreamFieldPanel('body'),
    ]

    pagesection_panels = [
        StreamFieldPanel('headingpanel'),
        StreamFieldPanel('sidepanel'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Hovedinnhold'),
        ObjectList(pagesection_panels, heading='Seksjoner'),
        ObjectList(Page.promote_panels, heading='Promovér'),
        ObjectList(
            Page.settings_panels,
            heading='Instillinger',
            classname='settings'
        ),
    ])
