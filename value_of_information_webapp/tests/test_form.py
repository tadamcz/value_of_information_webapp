import django_q
import pytest


@pytest.fixture
def lognormal_data():
	return {
		'max_iterations': 10_000,
		'lognormal_prior_ev': 5,
		'lognormal_prior_sd': 4,
		'study_sd_of_estimator': 2,
		'bar': 7,
	}


@pytest.fixture
def normal_data():
	return {
		'max_iterations': 10_000,
		'normal_prior_ev': 5,
		'normal_prior_sd': 4,
		'study_sd_of_estimator': 2,
		'bar': 7,
	}


@pytest.mark.django_db
class TestFormSubmission:
	def test_form_error(self, normal_data, client):
		del normal_data['bar']

		response = client.post("/", data=normal_data)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 0

	def test_normal(self, normal_data, client):
		response = client.post("/", data=normal_data)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 1

	def test_lognormal(self, lognormal_data, client):
		response = client.post("/", data=lognormal_data)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 1
