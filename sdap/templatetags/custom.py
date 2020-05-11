from django import template
from django.urls import reverse
from django.utils.html import format_html
register = template.Library()

@register.filter
def keyvalue(dict, key):
    return dict[key]

@register.simple_tag
def truncate(data, length, study_id):

    html = ""
    if length > len(data):
        html = ",<br>".join(data)
    else:
        data = data[0:length-1]
        html = ",<br>".join(data)
        html += "<br><a style='color:blue' href={}>[..More]</a>".format(reverse("studies:study_view", kwargs={"stdid": study_id}))

    return format_html(html)

@register.simple_tag
def val_to_set(study, key):
    set_val = set()
    for data in study.data.all():
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

@register.simple_tag
def get_jbrowse_link(jbrowse_data):
    tracks = [jbrowse_data.jbrowse_id]

    if jbrowse_data.species.jbrowse_data['sequence']:
        tracks.append(jbrowse_data.species.jbrowse_data['sequence']['jbrowse_id'])
    for track in jbrowse_data.species.jbrowse_data['annotations']:
        tracks.append(track['jbrowse_id'])

    base_url = "https://jbrowse-rgv.genouest.org/?data=data/sample_data/json/"
    full_url = base_url + jbrowse_data.species.jbrowse_name + "&tracks=" + ",".join(tracks)
    html = "<a style='color:blue' href='{}' target='_blank'>Genome browser <i class='fas fa-external-link-alt'></i></a>".format(full_url)

    return format_html(html)

