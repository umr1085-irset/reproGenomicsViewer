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

from sdap.files.models import File
from sdap.jobs.models import Job
from sdap.tools.models import Tool
from sdap.studies.models import ExpressionStudy

def HomeView(request):
    context = {}
    return render(request, 'pages/home.html',context)

def index(request):
    studies = ExpressionStudy.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('-created_at')
    return render(request, 'pages/index.html', {'studies':studies})

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

