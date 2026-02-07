from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "apps.user"

    def ready(self) -> None:
        from . import signals

        #return super().ready()
