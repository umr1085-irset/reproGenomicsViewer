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
