from django.apps import AppConfig


# class RewardsConfig(AppConfig):
#     name = 'apps.rewards'

# from django.apps import AppConfig


class RewardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rewards'

    def ready(self):
        from . import signals