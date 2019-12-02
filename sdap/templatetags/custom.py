from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def val_to_set(study, key):
    set_val = set()
    for data in study.data.all():
        if key == "species":
            set_val.add(data.get_species_display())
        else:
            set_val.add(getattr(data, key))
    return ",<br>".join(set_val)

