from django.apps import AppConfig
# from utils.agent2 import BaseChatbot
from utils.agent2 import PhiResponder

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    
    def ready(self):
        PhiResponder._initialize_once()
        # Import inside ready() to avoid AppRegistryNotReady error
        from django_celery_beat.models import PeriodicTask, IntervalSchedule

    #     schedule, created = IntervalSchedule.objects.get_or_create(
    #         every=5,
    #         period=IntervalSchedule.SECONDS,
    #     )
    #     PeriodicTask.objects.get_or_create(
    #         interval=schedule,
    #         name='Delete old unsaved rooms',
    #         task='users.tasks.delete_old_unsaved_rooms',
    #     )
