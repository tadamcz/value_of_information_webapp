import django_q
import pytest


@pytest.fixture
def lognormal_data():
	return {
		'max_iterations': 10_000,
		'lognormal_prior_ev': 5,
		'lognormal_prior_sd': 4,
		'signal_sd': 2,
		'bar': 7,
	}


@pytest.fixture
def normal_data():
	return {
		'max_iterations': 10_000,
		'normal_prior_ev': 5,
		'normal_prior_sd': 4,
		'signal_sd': 2,
		'bar': 7,
	}


@pytest.mark.django_db
class TestFormSubmission:
	SUBMIT_URL = "/submit"

	def test_form_error(self, normal_data, client):
		del normal_data['bar']

		response = client.post(self.SUBMIT_URL, data=normal_data, follow=True)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 0

	def test_normal(self, normal_data, client):
		response = client.post(self.SUBMIT_URL, data=normal_data, follow=True)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 1

	def test_lognormal(self, lognormal_data, client):
		response = client.post(self.SUBMIT_URL, data=lognormal_data, follow=True)

		assert response.status_code == 200
		assert django_q.tasks.queue_size() == 1
