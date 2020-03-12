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
def print_species_data(value):
    data = link_to_genome_browser([value])
    return format_html("{}".format(", ".join(data)))

def link_to_genome_browser(species_list):

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

    link_list = []
    for species in species_list:
        string = species
        if species in species_dict:
            string += " <a style='color:blue' href='{}' target='_blank'>(Genome browser <i class='fas fa-external-link-alt'></i>)</a>".format(base_rgv_url + species_dict[species])
        link_list.append(string)

    return link_list

