import os
import json
from datetime import datetime

from dal import autocomplete
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.views.generic import CreateView
from django.core import serializers


import pandas as pd
import numpy as np
import json
import statistics

import uuid
import shutil
from .models import ExpressionStudy, ExpressionData, Gene, Database
from .forms import *
from .graphs import getClasses, get_graph_data_full, get_graph_data_genes, getGenesNumber, getValues, getValuesExpression

class GeneAutocomplete(autocomplete.Select2QuerySetView):

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.symbol

    def get_queryset(self):
        query = self.q
        qs = Gene.objects.all()
        if query:
            qs = qs.filter(Q(symbol__icontains=query) | Q(synonyms__icontains=query)| Q(gene_id__icontains=query))
        return qs

def get_gene(request, gene_id):

    gene = get_object_or_404(Gene, id=gene_id)
    data = {'gene_id' : gene.gene_id, "symbol": gene.symbol, "homolog_id": gene.homolog_id, "ensembl_id": gene.ensemble_id}
    return JsonResponse(data)

def get_stud_db(request):
    db_ids  = request.GET.getlist('db_ids[]')    
    print (db_ids)
    db_ids = list(map(int, db_ids))
    print (db_ids)
    studies_list = []
    for db in db_ids :
        print(db)
        database =get_object_or_404(Database, id=db)
        print(database)
        studies = ExpressionStudy.objects.filter(database=database)
        studies_list.extend(studies)

    print(studies_list)

    table = render_to_string('studies/partial_study_table.html', {'studies': studies_list}, request)
    data = {'table_list' : table}

    return JsonResponse(data)

def index(request):
    """
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
            "age",
            "antibody",
            "mutant",
            "cell_sorted",
            "keywords",
    ]

    studies = ExpressionStudy.objects.exclude(data=None)
    form = ExpressionStudyFilterForm(studies=studies)
    table = render_to_string('studies/partial_study_table.html', {'studies': studies}, request)
    """
    studies = ExpressionStudy.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('-created_at')
    context = {'studies': studies, 'columns': "columns", 'table': "table"}
    return render(request, 'studies/index.html', context)

def document_select(request):

    #if not "id" in request.GET:
    #    return redirect(reverse("studies:index"))

    id_list = request.GET.getlist('db_ids[]')
    # Just in case
    if not all(x.isdigit() for x in id_list):
        return redirect(reverse("studies:index"))

    studies = ExpressionStudy.objects.filter(id__in=id_list)
    if studies.count() == 0:
        return redirect(reverse("studies:index"))

    
    table = render_to_string('studies/partial_document_table.html', {'studies': studies}, request)
    data = {'table_list' : table}
    return JsonResponse(data)

def show_graph(request):

    if not "document_id" in request.GET and not "study_id" in request.GET:
        return redirect(reverse("studies:index"))

    document_id = request.GET["document_id"]
    study_id = request.GET["study_id"]
    # Just in case
    if not document_id.isdigit() or not study_id.isdigit():
        return redirect(reverse("studies:index"))


    ##########################
    # File Statistique only for RGV files
    ##########################
    data = get_object_or_404(ExpressionData, id=document_id)

    data_stat = {}
    gene_info = getGenesNumber(data)
    classes = getClasses(data)
    samples =  getValues(data,['Sample'])
    data_stat["samples"] = len(samples['Sample'])
    samples = np.array(samples['Sample'])
    data_stat["class_name"] = []
    data_stat["gene_number"] = gene_info[0]
    data_stat["gene_type"] = gene_info[1]
    data_stat["class_cluster"] = []
    data_stat["mean_cell_cluster"] = []
    for class_ in classes :
        name = class_.replace('Class:','')
        data_stat["class_name"].append(name)
        groups = getValues(data, [class_])
        groups = np.array(groups[class_])
        _, idx = np.unique(groups, return_index=True)
        cells_cluster = []
        uniq_groups = groups[np.sort(idx)[::-1]] #
        data_stat["class_cluster"].append(len(uniq_groups))
        for cond in uniq_groups :
            val_= len(samples[np.where(groups == str(cond))[0]])
            cells_cluster.append(val_)
        mean_cell_cluster = statistics.median(cells_cluster)
        data_stat["mean_cell_cluster"].append(mean_cell_cluster)
        
    study = get_object_or_404(ExpressionStudy, id=study_id)
    form = GeneFilterForm()
    classes = getClasses(data)
    context = {'study': study, 'document': data, 'classes': classes, 'form': form, 'data_stat':data_stat}
    return render(request, 'studies/graph.html', context)

def get_graph_data(request):
    
    if not "document_id" in request.GET:
        return redirect(reverse("studies:index"))

    document_id = request.GET["document_id"]

    if not document_id.isdigit():
        return redirect(reverse("studies:index"))

    data = get_object_or_404(ExpressionData, id=document_id)

    selected_class = request.GET.get('selected_class', None)

    if "gene_id" in request.GET:
        data = get_graph_data_genes(data, selected_class, request.GET['gene_id'])
    else:
        data = get_graph_data_full(data, selected_class)
    return JsonResponse(data)

def get_group_info(request):

    group = request.GET.get('group',None)
    sample = request.GET.get('sample',None)
    document_id = request.GET.get('document',None)
    
    data = get_object_or_404(ExpressionData, id=document_id)

    selected_class = request.GET.get('selected_class', None)

    expression_values_group = getValuesExpression(data, selected_class, group)


    table = render_to_string('studies/partial_group_info.html', {'genes_list': expression_values_group}, request)
    data = {'list' : expression_values_group, 'group':group}



    return JsonResponse(data)


def render_table(request):

    data = {}
    studies = ExpressionStudy.objects.exclude(data=None)
    kwargs = {}
    for key, value in request.GET.items():
        if value:
            if key == "article":
                kwargs[key + "__icontains"] = [value]
            else:
                kwargs[key + "__contains"] = [value]

    studies = studies.filter(**kwargs)
    # Filter here
    table = render_to_string('studies/partial_study_table.html', {'studies': studies}, request)
    data['table'] = table
    return JsonResponse(data)

def autocomplete_genes(request):
    if request.is_ajax():
        query = request.GET.get('term','')
        qs = Gene.objects.all()
        qs = qs.filter(Q(symbol__icontains=query) | Q(synonyms__icontains=query)| Q(gene_id__icontains=query))
        results = []
        for gene in qs :
            results.append({gene.symbol:""})
        print(results)
        data = json.dumps(results)
    else:
        data="fail"

    
    return JsonResponse(data)
