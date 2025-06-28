from django.db import models
from django.contrib.auth import get_user_model
import uuid
# Create your models here.
User = get_user_model()


class ChatRoom(models.Model):
    TYPE_CHOICES = (
        ('advisior', 'Advisior'),
        ('agent', 'Agent'),
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    name = models.CharField(max_length=255, null=True, blank=True)
    is_saved = models.BooleanField(default=False)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, null=True, blank=True, default="advisior")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class ChatMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    prompt = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.prompt}"