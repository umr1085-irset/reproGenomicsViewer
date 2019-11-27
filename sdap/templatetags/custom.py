from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def val_to_set(study, key):
    set_val = set()
    for data in study.data.all():
        set_val.add(getattr(data, key))
    return ", ".join(set_val)

