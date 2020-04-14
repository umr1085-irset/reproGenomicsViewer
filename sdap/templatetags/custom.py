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
def print_species(value, name):
    data = link_to_genome_browser(value)
    return format_html("<p><b>{}</b> : {}</p><hr>".format(name, ", ".join(data)))

@register.simple_tag
def get_studies_jbrowse(study):
    if study.technology == ["scRNA-Seq"] or not study.data:
        return format_html("<p><b>Species</b> : {}</p><hr>".format(", ".join(study.species)))

    data = link_to_genome_browser(study.data.all())
    return format_html("<p><b>Species</b> : {}</p><hr>".format(", ".join(data)))

def link_to_genome_browser(data_list):
    # Will have duplicate if we have datasets with same species but different jbrowse url..

    base_rgv_url = "https://jbrowse-rgv.genouest.org/?data=data/sample_data/json/"

    url_dict = {}

    for data in data_list:
        species = data.species.name
        if data.has_jbrowse:
            j_url = base_rgv_url + data.species.jbrowse_name + "&tracks=" + data.jbrowse_id
            url = "<a style='color:blue' href='{}' target='_blank'>(Genome browser <i class='fas fa-external-link-alt'></i>)</a>".format(j_url)
            url_dict[species] = url
        elif not species in url_dict:
            url_dict[species] = ""

    url_list= []
    for key, value in url_dict.items():
        url_list.append("{} {}".format(key, value))

    return url_list

