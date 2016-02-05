from django import template
from django.core.urlresolvers import reverse
from django.contrib import admin

register = template.Library()


@register.simple_tag
def edit_link(obj):
    """
    Renders link to admin edit page of the object"""

    try:
        if type(obj) not in admin.site._registry:
            raise ValueError
        reverse_str = 'admin:{}_{}_change'.format(
            obj._meta.app_label,  obj._meta.module_name)
        url = reverse(reverse_str, args=[obj.id])
    except AttributeError:
        raise ValueError('obj must be a Django model instance')
    except ValueError:
        raise ValueError('obj must be registered in admin')
    return url
