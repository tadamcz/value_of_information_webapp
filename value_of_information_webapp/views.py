import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from django.http import QueryDict
from django.shortcuts import render
from forms import EmptyForm
from boltons.dictutils import FrozenDict
from django.core.cache import cache
from value_of_information_webapp.simulation_to_io import simulation_to_io
from value_of_information_webapp.utils import utils
import hashlib
import concurrent.futures
from example_simulation import simulation
from django.http import HttpResponse, JsonResponse
import django_q

def home(request):

    if request.method == 'POST':
        parameters = dict(request.POST)
        del parameters['csrfmiddlewaretoken']
        parameters = str(parameters)
        try:
            # Development
            application_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD']).decode().strip()
        except subprocess.CalledProcessError:
            # Production (with Dokku)
            application_hash = os.environ.get('GIT_REV')


        query_uid = application_hash+parameters
        # We use hashblib because we don't want Python hash randomization
        # see: https://docs.python.org/3/reference/datamodel.html#object.__hash__
        query_uid = hashlib.md5(query_uid.encode('utf-8')).hexdigest()

        task_id = django_q.tasks.async_task(simulation_to_io, simulation, max_iterations=10)

        return render(request, 'pages/home.html', context={
            'task_id': task_id,
            'form': EmptyForm()
        })

    return render(request, 'pages/home.html', context={
       'form':EmptyForm()
   })


def get_result(request, task_id):
    task = django_q.tasks.fetch(task_id)
    if task is None:
        q_size = django_q.tasks.queue_size()
        return JsonResponse({'done':False, 'queue_size':q_size})
    else:
        return JsonResponse({'done': True, 'console_output': task.result, 'success':task.success, 'time_taken':task.time_taken()})
