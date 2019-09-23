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
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages

import uuid
import shutil

from celery.result import AsyncResult

from guardian.shortcuts import get_objects_for_user
from sdap.tools.models import Tool, Category
import sdap.tools.forms as forms
from sdap.jobs.models import Job

from django.conf import settings

from time import sleep
# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.exclude(category_of=None)

def DetailView(request, toolid):
    model = Tool
    template_name = 'tools/detail.html'
    # Or 404
    tool = Tool.objects.get(id=toolid)
    # Get form attached to the tool
    # Need an error management here
    form_function = getattr(forms, tool.form_name)
    data = dict()
    if request.method == 'POST':
            data = request.POST
            # Do something here with the args
            task = print_command_line.delay(tool.id, data)
            create_job("test", "/bla", request.user, task.id)
            return(redirect(reverse("jobs:running_jobs")))
    else:
        arguments = tool.arguments
        form = form_function(arguments=arguments)
        context = {'tool': tool, 'form':form}
        return render(request, 'tools/detail.html', context)

def create_job(title, output, owner, task_id):
    # Add checks?
    job = Job(
            title = title,
            output = output,
            created_by = owner,
            celery_task_id = task_id
        )
    job.save()


# Move this to task.py
# THIS MAKES CELERYBEATS CRASH
#@app.task
def print_command_line(tool_id, args):
    tool = Tool.objects.get(id=tool_id)
    string = "Command line : {} {} {} ".format(tool.command_line, tool.path, tool.script_name)
    for argument in tool.arguments.all():
        if argument.label in args:
            string += "{} {} ".format(argument.parameter, str(args[argument.label]))
    print(string)
