from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth import get_user_model

# language
class Language(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=10, unique=True, null=False, blank=False)  # 'en', 'fr', etc.
    name = models.CharField(max_length=50, null=False, blank=False)  # 'English', 'French'

    def __str__(self):
        return self.name

    class Meta:
        db_table = "languages"
    
    
# User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('user', 'user'),
    )
    
    TYPE_CHOICES = (
        ('apple', 'Apple'),
        ('google', 'Google'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True, max_length=50, db_index=True)
    apple_uid = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=150, unique=False, db_index=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(null=True, max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', null=True, blank=True)
    gender = models.CharField(max_length=10)
    image = models.ImageField(null=True, upload_to="uploads/users/images")
    change_password_token = models.CharField(null=True, max_length=250)
    city = models.CharField(max_length=20, null=True)
    dob = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    corporate_code = models.CharField(max_length=15, blank=True, null=True)
    device_token = models.TextField(null=True, blank=True)
    token_expired = models.DateTimeField(null=True, blank=True)
    public_key = models.TextField(null=True)
    stripe_session_id = models.TextField(null=True, blank=True)
    provider = models.CharField(max_length=15, choices=TYPE_CHOICES, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


    def save(self, *args, **kwargs):
        self.username = self.username.replace(" ", "").lower()
        super().save(*args, **kwargs)
        
        
        
        
# Reset Password
class PasswordReset(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username}"