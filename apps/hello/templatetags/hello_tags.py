from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.simple_tag
def edit_link(obj):
    """
    Renders link to admin edit page of the object"""

    try:
        reverse_str = 'admin:{}_{}_change'.format(
            obj._meta.app_label,  obj._meta.module_name)
        url = reverse(reverse_str, args=[obj.id])
    except:
        raise ValueError('obj must be a Django model instance')
    return '<a href="{}">Edit (admin)</a>'.format(url)
