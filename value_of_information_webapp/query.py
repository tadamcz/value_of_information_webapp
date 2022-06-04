import hashlib
import os
import subprocess

import django_q
import numpy as np
import scipy
from django.http.request import QueryDict
from value_of_information.signal_cost_benefit import CostBenefitInputs, CostBenefitsExecutor

import value_of_information.utils
from value_of_information.simulation import SimulationInputs, SimulationExecutor

from value_of_information_webapp.forms import CostBenefitForm, SimulationForm
from value_of_information_webapp.models import CSVData, PersistedQuery
from value_of_information_webapp.to_buffer import to_buffer
from value_of_information_webapp.utils import utils


class Query:
	"""
	We need to use a few static methods in here, or the args that are serialized and stored in the db
	become huge.
	"""
	CONVERGENCE_TARGET = 0.05

	def __init__(self, query_dict: QueryDict):
		self.query_dict = query_dict
		self.bind_forms(query_dict)

	def bind_forms(self, query_dict):
		self.sim_form = SimulationForm(query_dict)
		self.cb_form = CostBenefitForm(query_dict)

	@staticmethod
	def create_executors(sim_form, cb_form):
		bar = sim_form.cleaned_data['bar']
		signal_sd = sim_form.cleaned_data['signal_sd']
		prior_family = sim_form.cleaned_data["prior_family"]
		force_explicit = sim_form.cleaned_data['force_explicit']

		if prior_family == "normal":
			prior_mu = sim_form.cleaned_data['normal_prior_ev']
			prior_sigma = sim_form.cleaned_data['normal_prior_sd']

			prior = scipy.stats.norm(prior_mu, prior_sigma)

		if prior_family == "lognormal":
			prior_ev = sim_form.cleaned_data['lognormal_prior_ev']
			prior_sd = sim_form.cleaned_data['lognormal_prior_sd']

			lnorm_prior_mu, lnorm_prior_sigma = utils.lognormal_mu_sigma(mean=prior_ev, sd=prior_sd)
			prior = value_of_information.utils.lognormal(lnorm_prior_mu, lnorm_prior_sigma)

		simulation_inputs = SimulationInputs(
			prior=prior,
			sd_B=signal_sd,
			bar=bar)

		sim_executor = SimulationExecutor(
			simulation_inputs, force_explicit=force_explicit
		)

		if cb_form.is_full():
			cb_inputs = CostBenefitInputs(
				**cb_form.cleaned_data
			)
			cb_executor = CostBenefitsExecutor(inputs=cb_inputs)
		else:
			cb_executor = None

		return sim_executor, cb_executor

	def send_to_queue(self, persisted_query_id):
		task_id = django_q.tasks.async_task(
			to_buffer,
			Query.q_function,
			callable_kwargs={
				'sim_form': self.sim_form,
				'cb_form': self.cb_form,
				'convergence_target': self.CONVERGENCE_TARGET,
				'persisted_query_id': persisted_query_id
			}
		)

		return task_id

	@staticmethod
	def q_function(sim_form, cb_form, convergence_target, persisted_query_id):
		"""
		We try to keep the args to this as light as possible
		"""
		sim_executor, cb_executor = Query.create_executors(sim_form, cb_form)

		return Query.execute(sim_executor, cb_executor,
							 convergence_target=convergence_target,
							 max_iterations=sim_form.cleaned_data['max_iterations'],
							 persisted_query_id=persisted_query_id)

	@staticmethod
	def execute(sim_executor, cb_executor, convergence_target, max_iterations, persisted_query_id):
		sim_run = sim_executor.execute(
			convergence_target=convergence_target,
			max_iterations=max_iterations
		)
		if cb_executor is not None:
			cb_executor.sim_run = sim_run
			cb_executor.execute()

		persisted_query = PersistedQuery.objects.get(pk=persisted_query_id)

		CSVData(query=persisted_query, string=sim_run.csv()).save()

		return {"mean_signal_benefit": sim_run.mean_benefit_signal()}

	def is_valid(self):
		simulation_form_valid = self.sim_form.is_valid()
		cost_benefit_form_valid = self.cb_form.is_valid()

		return simulation_form_valid and cost_benefit_form_valid

	def equivalence_class_id(self):
		"""
		Returns:
		hash(query+hash(application))

		Can be used to identify queries that should return the same results,
		(modulo sampling variation).

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
			application_hash = os.environ['GIT_REV']

		query_string = application_hash + parameters
		query_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest()

		return query_hash
