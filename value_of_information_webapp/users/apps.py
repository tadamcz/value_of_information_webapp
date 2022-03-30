from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "value_of_information_webapp.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import value_of_information_webapp.users.signals  # noqa F401
        except ImportError:
            pass
