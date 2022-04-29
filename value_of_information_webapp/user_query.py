import hashlib
import os
import subprocess

import django_q
import numpy as np
import scipy
from django.http.request import QueryDict

from value_of_information.simulation import SimulationInputs, SimulationExecutor
from value_of_information.study_cost_benefit import CostBenefitInputs, CostBenefitsExecutor
from value_of_information_webapp.forms import CostBenefitForm, SimulationForm
from value_of_information_webapp.to_buffer import to_buffer
from value_of_information_webapp.utils import utils


class UserQuery:
	CONVERGENCE_TARGET = 0.05

	def __init__(self, query_dict: QueryDict):
		self.query_dict = query_dict
		self.bind_forms(query_dict)

	def bind_forms(self, query_dict):
		self.sim_form = SimulationForm(query_dict)
		self.cb_form = CostBenefitForm(query_dict)

	def create_executors(self):
		bar = self.sim_form.cleaned_data['bar']

		study_sd_of_estimator = self.sim_form.cleaned_data['study_sd_of_estimator']

		normal_prior_mu = self.sim_form.cleaned_data['normal_prior_ev']
		normal_prior_sigma = self.sim_form.cleaned_data['normal_prior_sd']

		lognormal_prior_ev = self.sim_form.cleaned_data['lognormal_prior_ev']
		lognormal_prior_sd = self.sim_form.cleaned_data['lognormal_prior_sd']

		force_explicit = self.sim_form.cleaned_data['force_explicit']

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

		sim_executor = SimulationExecutor(
			simulation_inputs, force_explicit=force_explicit
		)

		if self.cb_form.is_full():
			cb_inputs = CostBenefitInputs(
				**self.cb_form.cleaned_data
			)
			cb_executor = CostBenefitsExecutor(inputs=cb_inputs)
		else:
			cb_executor = None

		self.cb_executor = cb_executor
		self.sim_executor = sim_executor

	def send_to_queue(self):
		query_uid = self.stable_hash()
		self.create_executors()
		count_group = django_q.tasks.count_group(query_uid)

		if count_group == 0:
			django_q.tasks.async_task(
				to_buffer,
				self.execute,
				group=query_uid,
			)
		elif count_group != 1:
			raise RuntimeError

		return query_uid

	def execute(self):
		sim_run = self.sim_executor.execute(
			convergence_target=self.CONVERGENCE_TARGET,
			max_iterations=self.sim_form.cleaned_data['max_iterations']
		)
		if self.cb_executor is not None:
			self.cb_executor.sim_run = sim_run
			self.cb_executor.execute()

	def is_valid(self):
		simulation_form_valid = self.sim_form.is_valid()
		cost_benefit_form_valid = self.cb_form.is_valid()

		return simulation_form_valid and cost_benefit_form_valid

	def stable_hash(self):
		"""
		We use hashblib because we don't want Python hash randomization
		see: https://docs.python.org/3/reference/datamodel.html#object.__hash__
		"""
		parameters = dict(self.query_dict)
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

		query_string = application_hash + parameters
		query_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest()

		return query_hash
