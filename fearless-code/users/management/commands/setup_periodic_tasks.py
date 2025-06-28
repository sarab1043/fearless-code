from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask

class Command(BaseCommand):
    help = 'Setup periodic tasks for the application'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.SECONDS,
        )
        
        task, created = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Delete old unsaved rooms',
            task='users.tasks.delete_old_unsaved_rooms',
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created periodic task'))
        else:
            self.stdout.write(self.style.SUCCESS('Periodic task already exists'))
