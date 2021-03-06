# Generated by Django 3.2.12 on 2022-05-09 16:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('value_of_information_webapp', '0002_persistedquery_created_at'),
	]

	operations = [
		migrations.AlterField(
			model_name='persistedquery',
			name='q_task_id',
			field=models.UUIDField(null=True),
		),
		migrations.CreateModel(
			name='CSVData',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('string', models.TextField()),
				('query', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
											   to='value_of_information_webapp.persistedquery')),
			],
		),
	]
