import os
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from mimetypes import guess_type
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

from django.template.loader import render_to_string
from django.http import JsonResponse

import pandas as pd

from sdap.files.models import File, Folder
from .forms import VisualisationArgumentForm

# Create your views here.
def index(request):

    folders = Folder.objects.filter(
            created_by= request.user,
            folder=None
       ).order_by('-created_at')

    files = File.objects.filter(
            created_by= request.user,
            folder=None
        ).order_by('-created_at')

    context = {'folders': folders, 'files': files}

    return render(request, 'files/index.html', context)


def subindex(request, folderid):


    previous_folder = Folder.objects.filter(
            created_by= request.user,
            folders=folderid
       )

    if previous_folder:
        back_url = reverse('files:subindex', kwargs={'folderid': previous_folder[0].id})
    else:
        back_url = reverse('files:index')

    folders = Folder.objects.filter(
            created_by= request.user,
            folder=folderid
       ).order_by('-created_at')

    files = File.objects.filter(
            created_by= request.user,
            folder=folderid
        ).order_by('-created_at')

    context = {'folders': folders, 'files': files, 'back_url': back_url}

    return render(request, 'files/index.html', context)

def view_file(request, fileid):

    # Check perm
    file = get_object_or_404(File, id=fileid)

    if not has_permission(request.user, file):
        return redirect('403/')
    # Need to make a list of available visualization tools based on type
    v_types = {
        'TEXT': ['Raw'],
        'IMAGE': ['Raw'],
        'CSV': ['Table', 'Pieplot', 'Barplot']
    }
    context = {'types': v_types[file.type], 'file': file}
    return render(request, 'files/visualize.html', context)


def get_visualization(request, fileid):

    file = get_object_or_404(File, id=fileid)
    if not has_permission(request.user, file):
        return redirect('403/')

    data = {}

    if request.method == 'POST':
        # Need to check form
        data = show_data(file, request.POST)
    else:
        visu_type = request.GET.get('type', '')
        if not visu_type:
            return redirect('403/')

        if visu_type == "Raw" or visu_type == "Table":
            data['data_table'] = ""
            form = VisualisationArgumentForm()
            context = {'form': form}
            data['form'] = render_to_string('files/form.html',
                context,
                request=request
            )

        else:
            # What if it's not tab separated?
            # Check file existence
            df = pd.read_csv(file.file, sep=",")
            if request.GET.get('transpose', False):
                df = df.transpose()
            df_head = df.head()
            table_content = df_head.to_html(classes=["table","table-bordered","table-striped"], justify='center', max_cols=10)
            data['data_table'] = table_content
            form = VisualisationArgumentForm(visu_type=visu_type, table=df)
            context = {'form': form}
            data['form'] = render_to_string('files/form.html',
                context,
                request=request
            )
    return JsonResponse(data)

def has_permission(user,file):
    # TODO: Manage group permissions here
    has_permission = False
    if file.created_by == user:
        has_permission = True

    return has_permission

def download_file(request, fileid):
    file_object = get_object_or_404(File, pk=fileid)
    owner = file_object.created_by

    if owner != request.user :
        return HttpResponseForbidden()
    else :
        filename = file_object.file.name.split('/')[-1]
        response = HttpResponse(file_object.file, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


def show_data(file, post_data):
    data = {}
    if file.type == "TEXT":
        content = ""
        with file.file.open('r') as f:
            for line in f.readlines():
                content += line + "<br>"
        data['content'] = content
    elif file.type == "IMAGE":
        content = "<img src='" + file.file.url + "'></img>"
        data['content'] = content
    elif file.type == "CSV":
        df = pd.read_csv(file.file, sep=",")
        if 'transposed' in post_data:
            df = df.transpose()
        if post_data['type'] == "Table":
            table_content = "<div class='table-responsive' >" + df.to_html(classes=["table","table-bordered","table-striped"], justify='center', max_cols=10) + "</div>"
            data['content'] = table_content
        elif post_data['type'] == "Pieplot":
            data['content'] = createJsonViewPiePlot(df, post_data["Yvalues"])
        elif post_data['type'] == "Barplot":
            data['content'] = createJsonViewBarPlot(df, post_data["Yvalues"])
    return data




def createJsonViewBarPlot(data, row_number):
    chart = {}
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['layout'] = {'showlegend': False,'yaxis':{'tickfont':10},'hovermode': 'closest'}
    chart['data'] = {
        'type': "bar",
        'x': data.columns.to_list(),
        'y': data.iloc[int(row_number), :].values.tolist()
    }

    return chart


def createJsonViewPiePlot(data, row_number):
    chart = {}
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['layout'] = {'showlegend': False,'yaxis':{'tickfont':10},'hovermode': 'closest'}
    chart['data'] = {
        'type': "pie",
        'labels': data.columns.to_list(),
        'values': data.iloc[int(row_number), :].values.tolist(),
        'textposition': 'inside'
    }
    return chart

