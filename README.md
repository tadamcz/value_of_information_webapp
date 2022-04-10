# Deployment

Deployed using [Dokku](https://github.com/dokku/dokku), currently on an AWS EC2 instance.

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

```shell
# In a first shell
poetry run python manage.py qcluster

# In another shell
poetry run python manage.py runserver
```

