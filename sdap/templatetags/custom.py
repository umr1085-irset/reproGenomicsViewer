from django import template
from django.utils.html import format_html
register = template.Library()

@register.filter
def keyvalue(dict, key):
    return dict[key]



@register.simple_tag
def val_to_set(study, key):
    set_val = set()
    for data in study.data.all():
        if key == "species":
            set_val.add(data.get_species_display())
        else:
            set_val.add(getattr(data, key))
    return ",<br>".join(set_val)

@register.simple_tag
def print_val(value, name, is_array=True):
    if value:
        if is_array:
            return format_html("<p><b>{}</b> : {}</p><hr>".format(name, ", ".join(value)))
        else:
            return format_html("<p><b>{}</b> : {}</p><hr>".format(name, value))
    else:
        return ""
