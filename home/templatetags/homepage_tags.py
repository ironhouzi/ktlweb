from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    return context['request'].site.root_page


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


@register.inclusion_tag('home/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    '''
    Retrieves the top menu items - the immediate children of the parent page The
    has_menu_children method is necessary because the bootstrap menu requires
    a dropdown class to be applied to a parent.
    '''
    menuitems = parent.get_children().live().in_menu()

    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)

    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, path=None):
    '''
    Retrieves the children of the top menu items for the drop downs.
    '''
    menuitems_children = parent.get_children().live().in_menu()

    for item in menuitems_children:
        item.active = (path.url.startswith(item.url) if path else False)


    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        'request': context['request'],
    }
