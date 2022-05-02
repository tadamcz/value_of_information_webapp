import json
import os
import time

import django_q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from value_of_information_webapp.forms import SimulationForm, CostBenefitForm
from value_of_information_webapp.models import PersistedQuery
from value_of_information_webapp.query import Query

QUERY_EQUIV_CLASSES = os.environ.get('QUERY_EQUIV_CLASSES', False)


def home(request):
	return render(request, 'pages/home.html', context={
		'simulation_form': SimulationForm(initial=SimulationForm.INITIAL),
		'cost_benefit_form': CostBenefitForm(initial=CostBenefitForm.INITIAL),
	})


def submit(request):
	if request.method == 'POST':
		query = Query(request.POST)

		if not query.is_valid():
			return render(request, 'pages/home.html', context={
				'simulation_form': query.sim_form,
				'cost_benefit_form': query.cb_form,
			})

		query_id = query.equivalence_class_id()
		if QUERY_EQUIV_CLASSES:
			persisted_query = PersistedQuery.objects.filter(equivalence_class_id=query_id).first()
			if persisted_query:
				return redirect(persisted_query)

		q_task_id = query.send_to_queue()

		raw_form_data = dict(request.POST.items())
		raw_form_data.pop("csrfmiddlewaretoken", None)

		persisted_query = PersistedQuery(
			equivalence_class_id=query_id,
			q_task_id=q_task_id,
			raw_form_data_json=json.dumps(raw_form_data)
		)
		persisted_query.save()

		return redirect(persisted_query)


def query(request, id):
	persisted_query = PersistedQuery.objects.get(id=id)
	no_op = lambda x: x
	forms_dict = json.loads(persisted_query.raw_form_data_json, parse_float=no_op, parse_int=no_op)
	sim_form = SimulationForm(forms_dict)
	cb_form = CostBenefitForm(forms_dict)

	return render(request, 'pages/home.html', context={
		'task_id': persisted_query.q_task_id.hex,
		# todo: this isn't correct when an in progress task has been submitted twice by the user
		'task_submitted': time.time(),
		'simulation_form': sim_form,
		'cost_benefit_form': cb_form,
	})


def task(request, id):
	task = django_q.tasks.fetch(id)

	if task is None:
		q_size = django_q.tasks.queue_size()
		return JsonResponse({'completed': False, 'queue_size': q_size, 'task_checked': time.time()})
	else:
		return JsonResponse(
			{'completed': True, 'console_output': task.result, 'success': task.success,
			 'time_taken': task.time_taken()})
