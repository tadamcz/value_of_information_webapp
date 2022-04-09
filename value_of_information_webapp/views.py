import hashlib
import os
import subprocess
import time

import django_q
import numpy as np
import scipy
from django.http import JsonResponse
from django.shortcuts import render
from value_of_information import Simulation

from forms import SimulationForm
from value_of_information_webapp.simulation_to_io import simulation_to_io

INITIAL_FORM_VALUES = {
	'max_iterations': 10,
	'lognormal_prior_mu': 1,
	'lognormal_prior_sigma': 1,
	'population_std_dev': 20,
	'study_sample_size': 100,
	'bar': 5,
}


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

		simulation_form = SimulationForm(request.POST)
		if not simulation_form.is_valid():
			return render(request, 'pages/home.html', context={
				'form': simulation_form
			})

		max_iterations = simulation_form.cleaned_data['max_iterations']
		study_sample_size = simulation_form.cleaned_data['study_sample_size']
		population_std_dev = simulation_form.cleaned_data['population_std_dev']
		bar = simulation_form.cleaned_data['bar']

		normal_prior_mu = simulation_form.cleaned_data['normal_prior_mu']
		normal_prior_sigma = simulation_form.cleaned_data['normal_prior_sigma']
		lognormal_prior_mu = simulation_form.cleaned_data['lognormal_prior_mu']
		lognormal_prior_sigma = simulation_form.cleaned_data['lognormal_prior_sigma']

		if normal_prior_mu is not None and normal_prior_sigma is not None:
			prior = scipy.stats.norm(normal_prior_mu, normal_prior_sigma)
		elif lognormal_prior_mu is not None and lognormal_prior_sigma is not None:
			prior = scipy.stats.lognorm(scale=np.exp(lognormal_prior_mu), s=lognormal_prior_sigma)
		else:
			raise Exception

		simulation = Simulation(
			prior=prior,
			study_sample_size=study_sample_size,
			population_std_dev=population_std_dev,
			bar=bar)

		task_id = django_q.tasks.async_task(simulation_to_io, simulation, max_iterations=max_iterations)

		return render(request, 'pages/home.html', context={
			'task_id': task_id,
			'task_submitted': time.time(),
			'form': simulation_form
		})

	return render(request, 'pages/home.html', context={
		'form': SimulationForm(
			initial=INITIAL_FORM_VALUES)
	})


def get_result(request, task_id):
	task = django_q.tasks.fetch(task_id)
	if task is None:
		q_size = django_q.tasks.queue_size()
		return JsonResponse({'completed': False, 'queue_size': q_size, 'task_checked': time.time()})
	else:
		return JsonResponse(
			{'completed': True, 'console_output': task.result, 'success': task.success,
			 'time_taken': task.time_taken()})
