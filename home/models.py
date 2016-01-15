from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.blocks import (
    TextBlock, StructBlock, StreamBlock, FieldBlock,
    CharBlock, RichTextBlock
)
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, InlinePanel,
    PageChooserPanel, StreamFieldPanel, TabbedInterface, ObjectList
)

from modelcluster.fields import ParentalKey


class LinkFields(models.Model):
    link_external = models.URLField(
        blank=True,
        verbose_name='Ekstern lenke',
        help_text='Lenke til en side utenfor ktl.no'
    )
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Intern lenke',
        help_text='Lenke til en side hos ktl.no'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Dokument-lenke',
        help_text='Lenke til et dokument'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_external'),
    ]

    class Meta:
        abstract = True


class FullWidthImageSliderItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='bilde',
        help_text=('Alle bildene bør være av samme størrelse'
                   ', og bredere enn 1500px')
    )

    panels = [
        ImageChooserPanel('image'),
    ]

    class Meta:
        abstract = True


class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text='Lenketittel')

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, 'Lenke'),
    ]

    class Meta:
        abstract = True


class IntroBox(LinkFields):
    header = models.CharField(
        'Overskrift', max_length=255, help_text='Kortfattet emneforklaring'
    )
    subtitle = models.CharField(
        'Undertittel', max_length=255, help_text='Kortfattet undertittel'
    )
    icon = models.CharField(
        'Ikon', max_length=50,
        help_text='Velg ikonnavn fra http://font-awesome.io/cheatsheet/'
    )

    panels = [
        MultiFieldPanel(LinkFields.panels, 'Lenke'),
        FieldPanel('header'),
        FieldPanel('subtitle'),
        FieldPanel('icon'),
    ]

    class Meta:
        abstract = True


class HomePageFullWidthImageSlider(Orderable, FullWidthImageSliderItem):
    page = ParentalKey(
        'home.HomePage', related_name='image_slider', verbose_name='side'
    )


class HomePageIntroBox(Orderable, IntroBox):
    page = ParentalKey(
        'home.HomePage', related_name='intro_boxes', verbose_name='side'
    )


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(
        'home.HomePage', related_name='related_links', verbose_name='side'
    )


class PullQuoteBlock(StructBlock):
    quote = TextBlock('sitat')
    attribution = CharBlock('tilegnelse')

    def __str__(self):
        return 'sitat'

    class Meta:
        icon = 'openquote'


class UpcomingEventCountChoiceField(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('3', 'Tre aktviteter'),
        ('5', 'Fem aktviteter'),
        ('7', 'Syv aktviteter'),
        ('10', 'Ti aktviteter'),
    ))


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Venstrejustér'),
        ('right', 'Høyrejustér'),
        # ('mid', 'Midtstill'),
        ('full', 'Full størrelse'),
    ))


class EventsBlock(StructBlock):
    count = UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')

    class Meta:
        icon = 'date'
        template='gcal/blocks/display_events.html'


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


class HomePage(Page):
    body = StreamField(HomePageStreamBlock(), verbose_name='hovedinnhold')
    sidepanel = StreamField(SidePanelStreamBlock(), verbose_name='sidepanel')

    class Meta:
        verbose_name = "hjemmeside"

    content_panels = [
        FieldPanel('title', classname='full tittel'),
        InlinePanel('image_slider', label='Bildefremviser i full bredde'),
        InlinePanel('intro_boxes',
                    label='Boks-elementer for hurtiglenker til viktige sider.'),
        StreamFieldPanel('body'),
        InlinePanel('related_links', label='Relatert lenke'),
    ]

    sidepanel_panels = [
        StreamFieldPanel('sidepanel'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Hovedinnhold'),
        ObjectList(sidepanel_panels, heading='Sidepanel'),
        ObjectList(Page.promote_panels, heading='Promovér'),
        ObjectList(
            Page.settings_panels,
            heading='Instillinger',
            classname='settings'
        ),
    ])
