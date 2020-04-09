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

    species_dict = {
        'Homo sapiens': 'hg38',
        'Macaca mulatta': 'rheMac8',
        'Mus musculus':'mm10',
        'Rattus norvegicus':'rn6',
        'Canis lupus familiaris': 'canFam3',
        'Bos taurus': 'bosTau8',
        'Sus scrofa': 'susScr3',
        'Gallus gallus': 'galGal5',
        'Danio rerio': 'danRer10'
    }

    base_rgv_url = "https://jbrowse-rgv.genouest.org/?data=data/sample_data/json/"

    url_dict = {}

    for data in data_list:
        species = data.get_species_display()
        if species in species_dict and data.jbrowse_id:
            j_url = base_rgv_url + species_dict[species] + "&tracks=" + data.jbrowse_id
            url = "<a style='color:blue' href='{}' target='_blank'>(Genome browser <i class='fas fa-external-link-alt'></i>)</a>".format(j_url)
            url_dict[species] = url
        elif not species in url_dict:
            url_dict[species] = ""

    url_list= []
    for key, value in url_dict.items():
        url_list.append("{} {}".format(key, value))

    return url_list

