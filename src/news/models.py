from django.db import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel

from wagtail.search import index
from home.models import AbstractHomePage

# TODO:
# [ ] Image resolver (check events or return default).
# [ ] Twitter integration (description max_length is therefore 140).
# [ ] RSS feed


class NewsEntryIndex(AbstractHomePage, Page):
    @property
    def news_entries(self):
        return NewsEntry.objects.live().descendant_of(self).order_by(
            '-first_published_at'
        )

    def get_context(self, request, parent_context=None):
        # pagination
        paginator = Paginator(self.news_entries, 10)

        try:
            news_entries = paginator.page(request.GET.get('page'))
        except PageNotAnInteger:
            news_entries = paginator.page(1)
        except EmptyPage:
            news_entries = paginator.page(paginator.num_pages)

        context = super().get_context(request, parent_context=parent_context)
        context['news_entries'] = news_entries

        return context

    def __str__(self):
        return 'Nyhetsoversikt'

    class Meta:
        verbose_name = 'Nyhetsoversikt'
        verbose_name_plural = 'Nyhetsoversikter'

    subpage_types = ['news.NewsEntry']


# NewsEntryIndex.promote_panels = Page.promote_panels
#
#
class NewsEntry(Page):
    description = models.CharField('Sammendrag', max_length=140)
    details = RichTextField('Beskrivelse', null=True, blank=True)
    event_page = models.ForeignKey(
        'gcal.EventPage',
        verbose_name='Google Calendar oppføring',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name='Bilde til nyhetsstrømmen',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def news_index(self):
        return self.get_ancestors().type(NewsEntryIndex).last()

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('details')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('details'),
        ImageChooserPanel('feed_image'),
        FieldPanel('event_page')
    ]

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Nyhet'
        verbose_name_plural = 'Nyheter'

    parent_page_types = ['news.NewsEntryIndex']
