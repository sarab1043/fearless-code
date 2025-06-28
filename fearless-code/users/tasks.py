from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from users.models import ChatRoom

logger = logging.getLogger(__name__)

@shared_task
def delete_old_unsaved_rooms():
    logger.info("TASK delete_old_unsaved_rooms STARTED")
    try:
        cutoff = timezone.now() - timedelta(hours=24)
        rooms = ChatRoom.objects.filter(is_saved=False, created_at__lt=cutoff)
        logger.info('Rooms deleting start')
        for room in rooms:
            logger.info(f"Deleted chat room with UUID: {room.uuid}")
            room.delete()
        
        logger.info('Rooms are deleted which are not saved.')
    except Exception as ex:
        logger.error(f"Error deleting old chat rooms: {str(ex)}")
        return "Error occurred while deleting chat rooms"