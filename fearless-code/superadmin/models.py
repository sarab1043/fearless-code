from django.db import models
import uuid
# Create your models here.

class Resources(models.Model):
    FILE_TYPES = [
        ("pdf", "PDF"),
        ("doc", "Document"),
        ("link", "Link"),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=10, choices=FILE_TYPES, null=True, blank=True)
    file = models.FileField(upload_to='uploads/resources/files/', null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='uploads/resources/thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}"