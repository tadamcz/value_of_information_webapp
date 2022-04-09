import datetime
import hashlib
import os
import subprocess
import time

import django_q
from django.http import JsonResponse
from django.shortcuts import render

from example_simulation import simulation
from forms import EmptyForm
from value_of_information_webapp.simulation_to_io import simulation_to_io


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

		query_uid = application_hash + parameters
		# We use hashblib because we don't want Python hash randomization
		# see: https://docs.python.org/3/reference/datamodel.html#object.__hash__
		query_uid = hashlib.md5(query_uid.encode('utf-8')).hexdigest()

		task_id = django_q.tasks.async_task(simulation_to_io, simulation, max_iterations=10)

		return render(request, 'pages/home.html', context={
			'task_id': task_id,
			'task_submitted': time.time(),
			'form': EmptyForm()
		})

	return render(request, 'pages/home.html', context={
		'form': EmptyForm()
	})


def get_result(request, task_id):
	task = django_q.tasks.fetch(task_id)
	if task is None:
		q_size = django_q.tasks.queue_size()
		return JsonResponse({'completed': False, 'queue_size': q_size, 'task_checked': time.time()})
	else:
		return JsonResponse(
			{'completed': True, 'console_output': task.result, 'success': task.success, 'time_taken': task.time_taken()})
