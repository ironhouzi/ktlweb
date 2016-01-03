from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailcore.blocks import (
    TextBlock, StructBlock, StreamBlock, FieldBlock,
    CharBlock, RichTextBlock
)
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, InlinePanel,
    PageChooserPanel, StreamFieldPanel
)

from modelcluster.fields import ParentalKey


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    # link_document = models.ForeignKey(
    #     'wagtaildocs.Document',
    #     null=True,
    #     blank=True,
    #     related_name='+'
    # )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        # elif self.link_document:
        #     return self.link_document.url
        else:
            return self.link_external

    panels = [
        PageChooserPanel('link_page'),
        FieldPanel('link_external'),
        # DocumentChooserPanel('link_document'),
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


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('home.HomePage', related_name='related_links')


class PullQuoteBlock(StructBlock):
    quote = TextBlock('sitat')
    attribution = CharBlock('tilegnelse')

    def __str__(self):
        return 'sitat'

    class Meta:
        icon = 'openquote'


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Venstrejustér'),
        ('right', 'Høyrejustér'),
        ('mid', 'Midtstill'),
        ('full', 'Full bredde'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock('bilde')
    caption = RichTextBlock('bildetekst')
    alignment = ImageFormatChoiceBlock()


class HomePageStreamBlock(StreamBlock):
    h2 = CharBlock('overskrift-stor', icon='title', classname='title')
    h3 = CharBlock('overskrift-mindre', icon='title', classname='title')
    h4 = CharBlock('overskrift-minst', icon='title', classname='title')
    intro = RichTextBlock('introduksjon', icon='pilcrow')
    paragraph = RichTextBlock('paragraf', icon='pilcrow')
    aligned_image = ImageBlock(label='Justert bilde', icon='image')
    pullquote = PullQuoteBlock(label='Sitat')
    # document = DocumentChooserBlock(icon='doc-full-inverse')


class HomePage(Page):
    body = StreamField(HomePageStreamBlock())

    class Meta:
        verbose_name = "hjemmeside"

HomePage.content_panels = [
    FieldPanel('title', classname='full tittel'),
    StreamFieldPanel('body'),
    InlinePanel('related_links', label='Relatert lenke'),
]

HomePage.promote_panels = Page.promote_panels
