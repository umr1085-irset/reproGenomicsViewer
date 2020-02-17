import os
import json
from datetime import datetime

from dal import autocomplete
from django.contrib.auth import get_user_model, get_user
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
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import CreateView
from django.core import serializers

from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_perms

import pandas as pd
import numpy as np
import statistics

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView

import uuid
import shutil
from .models import ExpressionStudy, ExpressionData, Gene, Database
from .forms import *
from .graphs import getClasses, get_graph_data_full, get_graph_data_genes, getValues, get_density_graph_data_full, get_density_graph_gene_data_full, get_violin_graph_gene_data_full, getGenesValues, getNbSampleByClass

def add_document(request, stdid):

    if not request.user.is_authenticated :
        return HttpResponseRedirect('/unauthorized')

    study = get_object_or_404(ExpressionStudy, id=stdid)
    if not check_edit_permissions(request.user, study):
        return HttpResponseRedirect('/unauthorized')

    data = {}
    context = {'study': study}
    if request.method == 'POST':
        form = ExpressionDataForm(request.POST, request.FILES)
        if form.is_valid():
            object = form.save(commit=False)
            object.created_by = request.user
            object.study = study
            object.save()
            data['redirect'] = reverse("studies:study_view", kwargs={"stdid": study.id})
            data['form_is_valid'] = True
        else:
            context['form_errors'] = form.errors
            data['form_is_valid'] = False
    else:
        form = ExpressionDataForm()

    context['form'] = form
    data['html_form'] = render_to_string('studies/partial_document_create.html',
        context,
        request=request,
    )

    return JsonResponse(data)

def download_document(request, documentid):
    doc = get_object_or_404(ExpressionData, id=documentid)

    if not check_view_permissions(request.user, doc.study):
        return redirect('/unauthorized')

    if not os.path.exists(doc.file.path):
        return redirect('/unauthorized')

    response = FileResponse(open(doc.file.path, 'rb'))
    response['Content-Type'] = "text/tab-separated-values"
    response['Content-Disposition'] = 'attachment; filename={}'.format(doc.name)
    response['Content-Transfer-Encoding'] = "binary"
    response['Content-Length'] = os.path.getsize(doc.file.path)

    return response

def delete_document(request, documentid):

    doc = get_object_or_404(ExpressionData, id=documentid)
    study = doc.study

    if not check_edit_permissions(request.user, study) or study.status == "PUBLIC":
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        doc.delete()
        data = {'form_is_valid': True, 'redirect': reverse("studies:study_view", kwargs={"stdid": study.id})}
    else:
       context = {'doc': doc}
       data['html_form'] = render_to_string('studies/partial_document_delete.html',
           context,
           request=request,
       )
    return JsonResponse(data)


def ExpressionStudyDetailView(request, stdid):
    study = get_object_or_404(ExpressionStudy, pk=stdid)
    if not check_view_permissions(request.user, study, True):
        return redirect('/unauthorized')
    context = {'study': study}
    if check_edit_permissions(request.user, study) and not study.status == "PUBLIC":
        context['has_edit_perm'] = True

    return render(request, 'studies/study_details.html', context)

class CreateExpressionStudyView(LoginRequiredMixin, CreateView):
    model = ExpressionStudy
    template_name = 'studies/study_create.html'
    form_class = ExpressionStudyCreateForm

    def get_form_kwargs(self):
        kwargs = super(CreateExpressionStudyView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    # Autofill the user
    def form_valid(self, form):
        array_fields_autocomplete = ['ome', 'experimental_design', 'topics', 'tissues', 'sex', 'dev_stage', 'antibody', 'mutant', 'cell_sorted']
        study = form.save(commit=False)
        # Manually force the array fields with autocomplete into a list
        for field in array_fields_autocomplete:
            # Hacky hacky.. I hate arrayfields
            if form.cleaned_data.get(field).strip() != '""':
                setattr(study, field, form.cleaned_data.get(field).strip().split(','))
            else:
                setattr(study, field, [])
        study.created_by = get_user(self.request)
        study.save()
        form.save_m2m()
        return redirect(reverse('studies:study_view', kwargs = {'stdid': study.id}))

class EditExpressionStudyView(PermissionRequiredMixin, UpdateView):
    # Only owner has delete_project perm
    permission_required = ['change_expressionstudy', 'delete_expressionstudy']
    model = ExpressionStudy
    login_url = "/unauthorized"
    redirect_field_name="edit"
    form_class = ExpressionStudyEditForm
    template_name = 'studies/study_edit.html'
    context_object_name = 'edit'

    def get_form_kwargs(self):
        kwargs = super(EditExpressionStudyView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_object(self, queryset=None):
        study = ExpressionStudy.objects.get(id=self.kwargs['stdid'])
        if study.status == "PUBLIC":
            return None
        else:
            return study

    def form_valid(self, form):
        array_fields_autocomplete = ['ome', 'experimental_design', 'topics', 'tissues', 'sex', 'dev_stage', 'antibody', 'mutant', 'cell_sorted']
        study = form.save(commit=False)
        # Manually force the array fields with autocomplete into a list
        for field in array_fields_autocomplete:
            if form.cleaned_data.get(field).strip():
                setattr(study, field, form.cleaned_data.get(field).strip().split(','))
            else:
                setattr(study, field, [])
        study.created_by = get_user(self.request)
        study.save()
        form.save_m2m()
        return redirect(reverse('studies:study_view', kwargs = {'stdid': study.id}))

def delete_study(request, stdid):

    study = get_object_or_404(ExpressionStudy, id=stdid)

    if not request.user == study.created_by or study.status == "PUBLIC":
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        study.delete()
        data = {'form_is_valid': True, 'redirect': reverse("users:detail", kwargs={"username": request.user.username})}
    else:
       context = {'study': study}
       data['html_form'] = render_to_string('studies/partial_study_delete.html',
           context,
           request=request,
       )
    return JsonResponse(data)

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

    all_studies = [study for study in ExpressionStudy.objects.exclude(data=None).order_by('article') if check_view_permissions(request.user, study)]
    studies = paginate(all_studies)
    form = ExpressionStudyFilterForm(studies=all_studies)
    table = render_to_string('studies/partial_study_table.html', {'studies': studies}, request)
    modal = render_to_string('studies/partial_study_modal.html', {'studies': studies}, request)
    pagination = render_to_string('studies/partial_study_pagination.html', {'table': studies}, request)
    context = {'form': form, 'columns': columns, 'table': table, 'pagination': pagination, 'modal': modal, 'data_type':'partial'}
    return render(request, 'studies/scatter_plot.html', context)

def document_select(request):

    if not "id" in request.GET:
        return redirect(reverse("studies:index"))

    id = request.GET["id"]
    # Just in case
    if not id.isdigit():
        return redirect(reverse("studies:index"))

    studies = ExpressionStudy.objects.filter(id=id)
    if studies.count() == 0:
        return redirect(reverse("studies:index"))

    return render(request, 'studies/document_select.html', {'study': studies[0]})

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

    data_stat = getNbSampleByClass(data)


    study = get_object_or_404(ExpressionStudy, id=study_id)
    form = GeneFilterForm()
    classes = getClasses(data)
    context = {'study': study, 'document': data, 'classes': classes, 'form': form, 'data_stat':data_stat}
    return render(request, 'studies/graph.html', context)

def get_graph_data(request):

    display_mode = "scatter"

    if "mode" in request.GET:
        display_mode = request.GET["mode"]


    if not "document_id" in request.GET:
        return redirect(reverse("studies:index"))

    document_id = request.GET["document_id"]

    if not document_id.isdigit():
        return redirect(reverse("studies:index"))

    data = get_object_or_404(ExpressionData, id=document_id)
    genelist = request.GET.getlist('gene_id', [])

    selected_class = request.GET.get('selected_class', None)

    if genelist :
        exp_list = []
        for g_ in genelist :
            gene = get_object_or_404(Gene, id=g_)
            exp_list.append(gene)
        if display_mode =="scatter" :
            data = get_graph_data_genes(data,exp_list, selected_class)
        if display_mode =="density" :
            data = get_density_graph_gene_data_full(data,exp_list, selected_class)
        if display_mode =="violin" :
            data = get_violin_graph_gene_data_full(data,exp_list, selected_class)
    else:
        if display_mode =="scatter" :
            data = get_graph_data_full(data, selected_class)
        if display_mode =="density" :
            data = get_density_graph_data_full(data, selected_class)
        if display_mode =="violin" :
            data = {'chart':[],'warning':[],'time':'',"error_msg":"Please select at least one gene"}
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
    type = request.GET.get('type')
    pagination = request.GET.get('pagination', 10)

    if type == "partial":
        studies = ExpressionStudy.objects.exclude(data=None)
    else:
        studies = ExpressionStudy.objects.all()
    kwargs = {}
    for key, value in request.GET.items():
        if value:
            if key == "article" or key == "keywords":
                kwargs[key + "__icontains"] = value
            elif key == "pmid":
                kwargs[key + "__istartswith"] = value
            elif key == "technology" or key == "species":
                kwargs["data__" + key] = value
            elif key == "page" or key == "type" or key == "pagination":
                continue
            else:
                kwargs[key + "__contains"] = [value]

    studies = paginate([study for study in studies.filter(**kwargs).distinct().order_by('article') if check_view_permissions(request.user, study)], request.GET.get('page'), pagination)
    # Filter here
    table = render_to_string('studies/partial_study_table.html', {'studies': studies}, request)
    modal = render_to_string('studies/partial_study_modal.html', {'studies': studies}, request)
    pagination = render_to_string('studies/partial_study_pagination.html', {'table': studies}, request)
    data['table'] = table
    data['pagination'] = pagination
    data['modal'] = modal
    return JsonResponse(data)

def autocomplete_genes(request,taxonid):

    if request.is_ajax():
        query = request.GET.get('term','')
        qs = Gene.objects.all()
        qs = qs.filter(Q(tax_id__exact=int(taxonid)))
        qs = qs.filter(Q(symbol__icontains=query) | Q(synonyms__icontains=query)| Q(gene_id__icontains=query) & Q(tax_id__exact=int(taxonid)))
        results = []
        for gene in qs :
            results.append({'label' : gene.symbol+" ("+str(gene.gene_id)+")", 'value': gene.id})
        data = json.dumps(results[:10])
    else:
        data="fail"
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def paginate(values, query=None, count=10, is_ES=False):

    if count == "all":
        paginator = Paginator(values, len(values))
    else:
        paginator = Paginator(values, count)

    try:
        val = paginator.page(query)
    except PageNotAnInteger:
        val = paginator.page(1)
    except EmptyPage:
        val = paginator.page(paginator.num_pages)

    return val

def check_view_permissions(user, study, strict=False):
    has_access = False
    if study.status == "PUBLIC" and not strict:
        has_access = True
    elif user.is_superuser:
        has_access = True
    elif user.is_authenticated and 'view_expressionstudy' in get_perms(user, study):
        has_access = True

    return has_access

def check_edit_permissions(user, study, need_owner=False):
    has_access = False

    if not need_owner:
        if user.is_authenticated and 'change_expressionstudy' in get_perms(user, study):
            has_access = True
    else:
        if user == study.created_by:
            has_access = True

    # Stop modification when public
    if study.status == "PUBLIC":
        has_access = False

    if user.is_superuser:
        has_access = True

    return has_access

def get_genes_values_table(request, document_id):

    warning = ""
    is_ok = False

    if request.method != 'POST':
        return

    if not request.POST.get('genes') or not request.POST.get('query') or not request.POST.get('class'):
        return

    document = get_object_or_404(ExpressionData, id=document_id)
    gene_list = request.POST.get('genes').replace('\n', ',').replace('\t', ',').split(',')
    selected_class= request.POST.get('class')
    correct_gene_dict = _process_gene_list(gene_list, document.species, request.POST.get('query'), document.gene_type)
    data = {}
    if correct_gene_dict:
        results = getGenesValues(document, selected_class, correct_gene_dict)
        is_ok = True
        data['dataset'] = results['results']
        data['columns'] = results['groups']
        data['base_table'] = render_to_string('studies/partial_genes_table.html', {'columns': data['columns']}, request)
    else:
        warning = "No corresponding genes in database: Have you selected the right data type (id or name)?"

    data['is_ok'] = is_ok
    data['warning'] = warning
    return JsonResponse(data)


def _process_gene_list(gene_list, species_id, query_type, target_gene_type):
    correct_dict = {}
    missing = []
    for gene in gene_list:
        correct_gene_id = _process_gene(gene, species_id, query_type, target_gene_type)
        if correct_gene_id:
            correct_dict[gene] = correct_gene_id
        else:
            correct_dict[gene] = ""
    return correct_dict

def _process_gene(gene_id, species_id, query_type, target_gene_type):

    correct_gene_id = ""

    # Assume they meant gene from the document species
    if query_type == "name":
        gene = Gene.objects.filter(symbol__iexact=gene_id, tax_id=species_id)
        if gene:
            if target_gene_type == "Entrez Gene":
                correct_gene_id = gene[0].gene_id
            else:
                correct_gene_id = gene[0].ensemble_id
    else:
    # Check ids
        if "ENS" in "gene_id":
            gene = Gene.objects.filter(ensemble_id__iexact=gene_id)
        else:
            gene = Gene.objects.filter(gene_id__iexact=gene_id)

        if gene:
            gene = gene[0]
            if gene.tax_id == "species_id":
                if target_gene_type == "Entrez Gene":
                    correct_gene_id = gene.gene_id
                else:
                    correct_gene_id = gene.ensemble_id
            else:
                correct_gene = Gene.objects.filter(homolog_id=gene.homolog_id, tax_id=species_id)
                if correct_gene:
                    correct_gene = correct_gene[0]
                    if target_gene_type == "Entrez Gene":
                        correct_gene_id = correct_gene.gene_id
                    else:
                        correct_gene_id = correct_gene.ensemble_id

    return correct_gene_id
