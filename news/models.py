from django.db import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField

from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtail.wagtailsearch import index

# TODO:
# [ ] Event FK.
# [ ] Event snippet chooser, on the fly creation using model clusters.
# [ ] Image resolver (check events or return default).
# [ ] Tagging.
# [ ] Twitter integration (description max_length is therefore 140).
# [ ] Search ???


class NewsEntryIndex(Page):
    @property
    def news_entries(self):
        return NewsEntry.objects.live().descendant_of(self).order_by('-date')

    def get_context(self, request):
        # pagination
        paginator = Paginator(self.news_entries, 10)

        try:
            news_entries = paginator.page(request.GET.get('page'))
        except PageNotAnInteger:
            news_entries = paginator.page(1)
        except EmptyPage:
            news_entries = paginator.page(paginator.num_pages)

        context = super().get_context(request)
        context['news_entries'] = news_entries

        return context

    def __str__(self):
        return 'Nyhetsoversikt'

    class Meta:
        verbose_name = 'Nyhetsoversikt'
        verbose_name_plural = 'Nyhetsoversikter'

    subpage_types = ['news.NewsEntry']


NewsEntryIndex.promote_panels = Page.promote_panels


class NewsEntry(Page):
    description = models.CharField('Beskrivelse', max_length=140)
    details = RichTextField('Detaljer', null=True, blank=True)
    date = models.DateField('Dato', auto_now=True, blank=False)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name='Bilde til nyhetsstrømmen',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    # event = models.ForeignKey(...)

    @property
    def news_index(self):
        return self.get_ancestors().type(NewsEntryIndex).last()

    search_fields = Page.search_fields + (
        index.SearchField('description'),
        index.SearchField('details'),
        index.FilterField('date'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('details'),
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('feed_image'),
    ]

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Nyhet'
        verbose_name_plural = 'Nyheter'

    parent_page_types = ['news.NewsEntryIndex']
