from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string

from sdap.files.models import File
from sdap.jobs.models import Job
from sdap.tools.models import Tool
from sdap.studies.models import ExpressionStudy, ExpressionData, GeneList
from sdap.studies.views import paginate, check_view_permissions
from sdap.studies.forms import ExpressionStudyFilterForm

from sdap.studies.graphs import getClasses

def HomeView(request):
    context = {}
    return render(request, 'pages/home.html',context)

def index(request):
    columns = [
            "article",
            "pmid",
            "ome",
            "technology",
            "species",
            "experimental_design",
            "topics",
            "tissues",
            "sex",
            "dev_stage",
            "antibody",
            "mutant",
            "cell_sorted",
            "keywords",
            "Select"
    ]
    all_studies =[study for study in  ExpressionStudy.objects.all().order_by('article') if check_view_permissions(request.user, study)]
    studies = paginate(all_studies)
    form = ExpressionStudyFilterForm(studies=all_studies)
    table = render_to_string('studies/partial_study_table.html', {'studies': studies}, request)
    modal = render_to_string('studies/partial_study_modal.html', {'studies': studies}, request)
    pagination = render_to_string('studies/partial_study_pagination.html', {'table': studies}, request)
    context = {'form': form, 'columns': columns, 'table': table, 'pagination': pagination, 'modal': modal, 'data_type': 'full'}
    return render(request, 'studies/scatter_plot.html', context)

def render_403(request):
    if request.GET.get('edit'):
        action = "edit"
        split = request.GET.get('edit').split('/')
        type = split[1]
    elif request.GET.get('create'):
        action = "create"
        split = request.GET.get('create').split('/')
        type = split[1]
    else:
        action = "view"
        type = ""
    data = {
        'action': action,
        'type': type
    }

    return render(request, '403_custom.html', {'data':data})

def _get_count(specie):
    studies = ExpressionStudy.objects.filter(species__contains=[specie])
    study_count = studies.count()
    sample_count = sum([study.samples_count for study in studies])
    return study_count, sample_count

def genome_browser(request):

    species = {
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

    data = []
    base_rgv_url = "https://jbrowse-rgv.genouest.org/?data=data/sample_data/json/"
    base_ucsc_url = "https://genome.ucsc.edu/cgi-bin/hgTracks?db="


    for key, value in species.items():
        dict = {
            'name': key,
            'short': value,
            'image': 'images/species/' + value + '.png',
            'rgv_url': base_rgv_url + value,
            'ucsc_url': base_ucsc_url + value,
        }

        dict['studies'], dict['samples'] = _get_count(key)
        data.append(dict)

    return render(request, 'pages/genome_browser.html', {'species': data} )

def golden(request):
    document = ExpressionData.objects.get(id=152)
    study = document.study
    context = {'study': study, 'data': document, 'document': document, 'classes': getClasses(document)}
    if request.user.is_authenticated:
        context['gene_list'] = GeneList.objects.filter(created_by=request.user, species=document.species)
    else:
        context['gene_list'] = []

    return render(request, 'pages/test.html', context )
