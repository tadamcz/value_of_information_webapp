# Generated by Django 3.2.12 on 2022-04-09 10:48

from django.db import migrations


class Migration(migrations.Migration):
	dependencies = [
		('sites', '0002_alter_domain_unique'),
	]

	operations = [
		migrations.AlterModelOptions(
			name='site',
			options={'ordering': ['domain'], 'verbose_name': 'site', 'verbose_name_plural': 'sites'},
		),
	]
