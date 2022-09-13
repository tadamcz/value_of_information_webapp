# Code structure

A Django app that acts as a wrapper around the package `value-of-information` ([tadamcz/value-of-information](https://github.com/tadamcz/value-of-information)).

That package is included as a git submodule, and listed in `pyproject.toml` as a local dependency in editable mode. You'll need to initialize and update that submodule. It's easiest to do this at the beginning by passing `--recurse-submodules` to the `git clone` command. 

The initial skeleton was set up using Cookiecutter Django. See `README_cookiecutter.md`.

The best entrypoint into the code is probably `value_of_information_webapp/views.py`.

# Deployment

Deployed using [Dokku](https://github.com/dokku/dokku), currently on an AWS EC2 instance. The files used by Dokku are `.buildpacks`, `.env`, and `app.json`.

# Local development

## Installation

```shell
git clone --recurse-submodules git@github.com:tadamcz/value_of_information_webapp.git
poetry install
```

```shell
poetry run python manage.py migrate # uses SQLite locally
```

## Execution

The application uses a task queue. The workers processing the tasks need to be started separately with `manage.py qcluster`.

```shell
# In a first shell
poetry run python manage.py qcluster

# In another shell
poetry run python manage.py runserver
```


# Origin of this project
This tool was developed under contract for [Open Philanthropy](https://www.openphilanthropy.org/). Open Philanthropy plans to use this tool as one input into the decision of whether to fund randomized trials in global health or development. Because the concept is quite general, we hope that the tool can also be useful to others.