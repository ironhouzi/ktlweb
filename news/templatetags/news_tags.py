from django import template
from news.models import NewsEntry


register = template.Library()


@register.inclusion_tag('news/tags/newsentry.html')
def news_entry(count='4'):
    count = int(count)
    all_entries = NewsEntry.objects.filter(live=True
                                           ).order_by('-first_published_at'
                                                      )[:count]

    result = {
        'latest_news': None,
        'secondary_news': None
    }

    if all_entries.count() > 0:
        result['latest_news'] = all_entries[0],
        result['secondary_news'] = all_entries[1:]

    return result
