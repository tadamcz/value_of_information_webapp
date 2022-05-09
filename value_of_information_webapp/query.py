import hashlib
import os
import subprocess

import django_q
import numpy as np
import scipy
from django.http.request import QueryDict

from value_of_information.simulation import SimulationInputs, SimulationExecutor
from value_of_information.signal_cost_benefit import CostBenefitInputs, CostBenefitsExecutor
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

		normal_prior_mu = sim_form.cleaned_data['normal_prior_ev']
		normal_prior_sigma = sim_form.cleaned_data['normal_prior_sd']

		lognormal_prior_ev = sim_form.cleaned_data['lognormal_prior_ev']
		lognormal_prior_sd = sim_form.cleaned_data['lognormal_prior_sd']

		force_explicit = sim_form.cleaned_data['force_explicit']

		if normal_prior_mu is not None and normal_prior_sigma is not None:
			prior = scipy.stats.norm(normal_prior_mu, normal_prior_sigma)
		elif lognormal_prior_ev is not None and lognormal_prior_sd is not None:
			lnorm_prior_mu, lnorm_prior_sigma = utils.lognormal_mu_sigma(mean=lognormal_prior_ev, sd=lognormal_prior_sd)
			prior = scipy.stats.lognorm(scale=np.exp(lnorm_prior_mu), s=lnorm_prior_sigma)
		else:
			raise Exception

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
			callable_kwargs = {
				'sim_form': self.sim_form,
				'cb_form': self.cb_form,
				'convergence_target': self.CONVERGENCE_TARGET,
				'persisted_query_id':persisted_query_id
			}
		)

		return task_id

	@staticmethod
	def q_function(sim_form, cb_form, convergence_target, persisted_query_id):
		"""
		We try to keep the args to this as light as possible
		"""
		sim_executor, cb_executor = Query.create_executors(sim_form, cb_form)

		Query.execute(sim_executor, cb_executor,
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
