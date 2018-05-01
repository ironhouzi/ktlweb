from django import forms
from django.db import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.safestring import mark_safe

from markdown import markdown

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.core.blocks import (
    TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock,
    ListBlock, URLBlock, PageChooserBlock, BooleanBlock
)
from wagtail.admin.edit_handlers import (
    FieldPanel, StreamFieldPanel, TabbedInterface, ObjectList
)
from wagtail.search import index
from wagtail.utils.decorators import cached_classmethod


class PullQuoteBlock(StructBlock):
    quote = RichTextBlock(label='Sitat')
    attribution = CharBlock(label='Tilegnelse', required=False)

    def __str__(self):
        return 'sitat'

    class Meta:
        icon = 'openquote'


class HorizontalRulerBlock(StructBlock):
    def __str__(self):
        return 'skillestrek'

    class Meta:
        icon = 'horizontalrule'


class UpcomingEventCountChoiceField(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ('3', 'Tre aktviteter'),
            ('5', 'Fem aktviteter'),
            ('7', 'Syv aktviteter'),
            ('10', 'Ti aktviteter'),
        )
    )


class NewsFeedCountChoiceField(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ('4', 'Fire nyheter'),
        )
    )


class UpcomingEventCentreChoiceField(FieldBlock):
    field = forms.ChoiceField(
        choices=(
            ('ALL', 'Alle kalendre'),
            ('KTL', 'Kalender for KTL'),
            ('KSL', 'Kalender for KSL'),
            ('PM', 'Kalender for Paramita'),
        ),
        initial='ALL'
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


class NewsFeedBlock(StructBlock):
    count = NewsFeedCountChoiceField(label='Antall nyheter i visning')

    class Meta:
        icon = 'media'
        template = 'news/blocks/news_feed.html'
        help_text = (
            'Ved å aktivere dette valget vil siste nyheter vises.'
        )


class EventsBlock(StructBlock):
    count = UpcomingEventCountChoiceField(label='Antall synlige aktiviteter')
    centre_code = UpcomingEventCentreChoiceField(label='Hvilket senter?')
    display_all = BooleanBlock(label='Langtidsvisning', required=False)

    class Meta:
        icon = 'date'
        template = 'gcal/blocks/display_events.html'
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


class CommonLinkBlock(StructBlock):
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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
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
        abstract = True


class QuickLinkBlock(CommonLinkBlock):
    class Meta:
        icon = 'link'
        template = 'home/blocks/quicklink.html'


class SidepanelLinkBlock(CommonLinkBlock):
    class Meta:
        icon = 'link'
        template = 'home/blocks/sidepanel_link.html'


class ImageBannerBlock(StructBlock):
    image = ImageChooserBlock(label='Bilde')

    class Meta:
        icon = 'image'
        template = 'home/blocks/banner_image.html'


class ImageSliderBlock(StructBlock):
    image = ImageChooserBlock(label='Bilde')

    class Meta:
        icon = 'image'
        template = 'home/blocks/slider_image.html'


class ImageBlock(StructBlock):
    image = ImageChooserBlock(label='Bilde')
    caption = RichTextBlock(label='Bildetekst')
    alignment = ImageFormatChoiceBlock(label='Justering')


class MarkDownBlock(TextBlock):
    class Meta:
        icon = 'code'

    def render_basic(self, value, context=None):
        md = markdown(
            value,
            [
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )

        return mark_safe(md)


class VideoBlock(StructBlock):
    caption = TextBlock(label='Seksjonstittel', required=True)
    video_id = TextBlock(label='Youtube video-id', required=True)

    class Meta:
        icon = 'media'
        template = 'home/blocks/sidepanel_video.html'


class HomePageStreamBlock(StreamBlock):
    h2styled = CharBlock(
        label='stilisert overskrift',
        icon='title',
        classname='title'
    )
    h2 = CharBlock(label='overskrift stor', icon='title', classname='title')
    h3 = CharBlock(label='overskrift mindre', icon='title', classname='title')
    h4 = CharBlock(label='overskrift minst', icon='title', classname='title')
    hr = HorizontalRulerBlock()
    intro = RichTextBlock(label='introduksjon', icon='pilcrow')
    paragraph = RichTextBlock(label='paragraf', icon='pilcrow')
    pullquote = PullQuoteBlock(label='Sitat')
    aligned_image = ImageBlock(label='Justert bilde', icon='image')
    document = DocumentChooserBlock(label='dokument', icon='doc-full-inverse')
    markdown = MarkDownBlock(label='markdown')
    news_feed = NewsFeedBlock(label='Siste nyheter', icon='grip')


class SidePanelStreamBlock(StreamBlock):
    eventviewer = EventsBlock(label='Vis kommende aktiviteter')
    linkviewer = ListBlock(
        SidepanelLinkBlock(),
        icon='link',
        label='Lenke- fremviser',
        template='home/blocks/sidepanel_links.html'
    )
    videoembed = VideoBlock(label='Youtube- video')


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
    bannerimage = ImageBannerBlock(
        label='Bannerbilde.\nOBS: 2048x500 piksler!'
    )


class AbstractHomePage(models.Model):
    body = StreamField(
        HomePageStreamBlock(required=False),
        verbose_name='hovedinnhold',
        default='',
        blank=True
    )
    headingpanel = StreamField(
        HeadingPanelStreamBlock(required=False),
        verbose_name='overpanel',
        default='',
        blank=True
    )
    sidepanel = StreamField(
        SidePanelStreamBlock(required=False),
        verbose_name='sidepanel',
        default='',
        blank=True
    )

    class Meta:
        abstract = True

    search_fields = Page.search_fields + [index.SearchField('body')]

    content_panels = Page.content_panels + [StreamFieldPanel('body')]

    pagesection_panels = [
        StreamFieldPanel('headingpanel'),
        StreamFieldPanel('sidepanel'),
    ]

    @cached_classmethod
    def get_edit_handler(cls):
        edit_handler = TabbedInterface([
            ObjectList(cls.content_panels, heading='Hovedinnhold'),
            ObjectList(cls.pagesection_panels, heading='Seksjoner'),
            ObjectList(cls.promote_panels, heading='Fremming'),
            ObjectList(
                cls.settings_panels,
                heading='Instillinger',
                classname='settings'
            ),
        ])

        return edit_handler.bind_to_model(cls)


class HomePage(AbstractHomePage, Page):
    class Meta:
        verbose_name = 'Hjemmeside'
        verbose_name_plural = 'Hjemmesider'


class ArticleIndex(AbstractHomePage, Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name='Bilde (1200x400)',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Bildet må være minst 1200x400 piksler og ha formatet 3x1.'
    )

    content_panels = [
        AbstractHomePage.content_panels[0],     # title
        ImageChooserPanel('image'),
        AbstractHomePage.content_panels[-1]     # streamfield
    ]

    @property
    def article_entries(self):
        order = '-first_published_at'
        return self.get_children().live().order_by(order).specific()

    def get_context(self, request, parent_context=None):
        # pagination
        paginator = Paginator(self.article_entries, 10)

        try:
            article_entries = paginator.page(request.GET.get('page'))
        except PageNotAnInteger:
            article_entries = paginator.page(1)
        except EmptyPage:
            article_entries = paginator.page(paginator.num_pages)

        context = super().get_context(request, parent_context=parent_context)
        context['article_entries'] = article_entries

        return context

    def __str__(self):
        return 'Artikkelindeks: {}'.format(self.id)

    class Meta:
        verbose_name = 'Artikkelindeks'
        verbose_name_plural = 'Artikkelindekser'

    subpage_types = ['home.Article', 'home.ArticleIndex']


class Article(AbstractHomePage, Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name='Bilde (1200x400)',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Bildet må være minst 1200x400 piksler og ha formatet 3x1.'
    )
    intro = models.TextField(
        'Ingress',
        null=True,
        blank=False,
        help_text='Kortfattet introduksjon, maks 4 linjer!'
    )
    other_author = models.TextField(
        'Annen forfatter',
        null=True,
        blank=True,
        help_text='Brukes kun om forfatter er noen andre enn deg selv.'
    )

    @property
    def author(self):
        return self.other_author or self.owner.get_full_name()

    @property
    def article_index(self):
        return self.get_ancestors().type(ArticleIndex).last()

    search_fields = AbstractHomePage.search_fields + [
        index.SearchField('intro')
    ]

    content_panels = [
        AbstractHomePage.content_panels[0],     # title
        FieldPanel('intro'),
        ImageChooserPanel('image'),
        FieldPanel('other_author'),
        AbstractHomePage.content_panels[-1]     # streamfield
    ]

    def __str__(self):
        return '<Article: {}>'.format(self.title)

    class Meta:
        verbose_name = 'Artikkel'
        verbose_name_plural = 'Artikler'

    parent_page_types = ['home.ArticleIndex']
