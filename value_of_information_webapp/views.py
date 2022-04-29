import time

import django_q
from django.http import JsonResponse
from django.shortcuts import render

from value_of_information_webapp.forms import SimulationForm, CostBenefitForm
from value_of_information_webapp.user_query import UserQuery


def home(request):
	if request.method == 'POST':
		user_query = UserQuery(request.POST)

		if not user_query.is_valid():
			return render(request, 'pages/home.html', context={
				'simulation_form': user_query.sim_form,
				'cost_benefit_form': user_query.cb_form,
			})

		query_uid = user_query.send_to_queue()

		return render(request, 'pages/home.html', context={
			'task_id': query_uid,
			# todo: this isn't correct when an in progress task has been submitted twice by the user
			'task_submitted': time.time(),
			'simulation_form': user_query.sim_form,
			'cost_benefit_form': user_query.cb_form,
		})

	return render(request, 'pages/home.html', context={
		'simulation_form': SimulationForm(initial=SimulationForm.INITIAL),
		'cost_benefit_form': CostBenefitForm(initial=CostBenefitForm.INITIAL),
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
