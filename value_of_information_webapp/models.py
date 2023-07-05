from django.db import models


class PersistedQuery(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	q_task_id = models.UUIDField(null=True)
	raw_form_data_json = models.CharField(max_length=10_000)

	# equal to: hash(query+hash(application))
	#
	# Can be used to identify queries that should return the same results,
	# (modulo sampling variation).
	equivalence_class_id = models.CharField(max_length=32)

	def get_absolute_url(self):
		return f'query/{self.id}'

	class Meta:
		indexes = [
			models.Index(fields=['equivalence_class_id'])
		]


class CSVData(models.Model):
	query = models.OneToOneField(PersistedQuery, on_delete=models.CASCADE)
	string = models.TextField()
