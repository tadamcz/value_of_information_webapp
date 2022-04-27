import hashlib
import os
import subprocess
import time

import django_q
import numpy as np
import scipy
from django.http import JsonResponse
from django.shortcuts import render

from value_of_information_webapp.forms import SimulationForm, CostBenefitForm
from value_of_information.simulation import SimulationInputs, SimulationExecutor
from value_of_information.study_cost_benefit import CostBenefitInputs, CostBenefitsExecutor
from value_of_information_webapp.to_buffer import to_buffer
from value_of_information_webapp.utils import utils

SIM_FORM_INITIAL = {
	'max_iterations': 10_000,
	'lognormal_prior_ev': 5,
	'lognormal_prior_sd': 4,
	'study_sd_of_estimator': 2,
	'bar': 7,
	'force_explicit': False,
}
C_B_FORM_INITIAL = {
	'value_units': 'utils',
	'money_units': 'M$',
	'capital': 100,
	'study_cost': 5,
}


def home(request):
	if request.method == 'POST':
		parameters = dict(request.POST)
		try:
			del parameters['csrfmiddlewaretoken']
		except KeyError:
			pass
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
		cost_benefit_form = CostBenefitForm(request.POST)

		simulation_form_valid = simulation_form.is_valid()
		cost_benefit_form_valid = cost_benefit_form.is_valid()

		if not simulation_form_valid or not cost_benefit_form_valid:
			return render(request, 'pages/home.html', context={
				'simulation_form': simulation_form,
				'cost_benefit_form': cost_benefit_form,
			})

		# todo refactor
		max_iterations = simulation_form.cleaned_data['max_iterations']
		bar = simulation_form.cleaned_data['bar']

		study_sd_of_estimator = simulation_form.cleaned_data['study_sd_of_estimator']

		normal_prior_mu = simulation_form.cleaned_data['normal_prior_ev']
		normal_prior_sigma = simulation_form.cleaned_data['normal_prior_sd']

		lognormal_prior_ev = simulation_form.cleaned_data['lognormal_prior_ev']
		lognormal_prior_sd = simulation_form.cleaned_data['lognormal_prior_sd']

		force_explicit = simulation_form.cleaned_data['force_explicit']

		if normal_prior_mu is not None and normal_prior_sigma is not None:
			prior = scipy.stats.norm(normal_prior_mu, normal_prior_sigma)
		elif lognormal_prior_ev is not None and lognormal_prior_sd is not None:
			lnorm_prior_mu, lnorm_prior_sigma = utils.lognormal_mu_sigma(mean=lognormal_prior_ev, sd=lognormal_prior_sd)
			prior = scipy.stats.lognorm(scale=np.exp(lnorm_prior_mu), s=lnorm_prior_sigma)
		else:
			raise Exception

		simulation_inputs = SimulationInputs(
			prior=prior,
			sd_B=study_sd_of_estimator,
			bar=bar)

		simulation_executor = SimulationExecutor(
			simulation_inputs, force_explicit=force_explicit
		)

		if cost_benefit_form.is_full():
			cb_inputs = CostBenefitInputs(
				**cost_benefit_form.cleaned_data
			)
			c_b_executor = CostBenefitsExecutor(inputs=cb_inputs)
		else:
			c_b_executor = None

		count_group = django_q.tasks.count_group(query_uid)
		if count_group == 0:
			django_q.tasks.async_task(
				to_buffer,
				sim_executor=simulation_executor,
				c_b_executor=c_b_executor,
				max_iterations=max_iterations,
				convergence_target=0.05,
				group=query_uid,
			)
		elif count_group != 1:
			raise RuntimeError

		return render(request, 'pages/home.html', context={
			'task_id': query_uid,
			'task_submitted': time.time(),  # todo: this isn't correct when an in progress task has been submitted twice by the user
			'simulation_form': simulation_form,
			'cost_benefit_form': cost_benefit_form,
		})

	return render(request, 'pages/home.html', context={
		'simulation_form': SimulationForm(initial=SIM_FORM_INITIAL),
		'cost_benefit_form': CostBenefitForm(initial=C_B_FORM_INITIAL),
	})


def get_result(request, query_uid):
	task_group = django_q.tasks.fetch_group(query_uid)

	if task_group is None:
		q_size = django_q.tasks.queue_size()
		return JsonResponse({'completed': False, 'queue_size': q_size, 'task_checked': time.time()})
	else:
		if len(task_group) == 1:
			task = task_group[0]
		else:
			raise RuntimeError

		return JsonResponse(
			{'completed': True, 'console_output': task.result, 'success': task.success,
			 'time_taken': task.time_taken()})
