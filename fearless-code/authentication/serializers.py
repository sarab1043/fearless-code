from rest_framework import serializers
from fearless_code import settings
from utils.constants import *
from utils.utils import generate_random_string
from .models import PasswordReset, User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
import os
import logging
logger = logging.getLogger(__name__)



# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}
    
    
    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super().create(validated_data)


# user details
class UserSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "uuid",
            "name",
            "email",
            "phone",
            "image",
            "role",
            "city",
            "is_active",
            "email_verified",
            "dob",
            "provider",
            "language",
            "date_joined"
        ]
        extra_kwargs = {"password": {"write_only": True}}
        
    def get_language(self, obj):
        return obj.language.code if obj.language else ''
    
    def get_date_joined(self, obj):
        return obj.date_joined if obj.date_joined else ''
    
    #get image
    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ''
    
    #update image
    def update(self, instance, validated_data):
        request = self.context.get("request")
        image = request.FILES.get("image") if request else None

        if image:
         
            if instance.image and instance.image.path and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
                  
            original_file_name = image.name
            file_extension = original_file_name.split(".")[-1]
            unique_name = generate_random_string(6)
            new_image_name = f"{unique_name}.{file_extension}"

            fs = FileSystemStorage(location=settings.MEDIA_ROOT / "uploads/users/images/")
            fs.save(new_image_name, image)

            # Save relative path inside MEDIA_ROOT
            instance.image = f"uploads/users/images/{new_image_name}"

        return super().update(instance, validated_data)

    
# User Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    
    
    def validate(self, data):
        email = data.get("email").lower()
        password = data.get("password")
        user = None        
        if email and password:
            is_email = "@" in email
            if is_email:
                user = authenticate(email=email, password=password)
            else:
                try:
                    get_user = User.objects.get(email=email)
                    user = authenticate(email=get_user.email, password=password)
                except User.DoesNotExist:
                    raise serializers.ValidationError(INCORRECT_USERNAME_EMAIL_PASSWORD)

        else:
            raise serializers.ValidationError(PASSWORD_REQUIRED_FIELDS)

        if user:
            if not user.is_active:
                raise serializers.ValidationError(USER_IS_INACTIVE)
            if not user.email_verified:
                raise serializers.ValidationError(USER_IS_UNVERIFIED)
            
            return {
                "user": user,
            }
        else:
            raise serializers.ValidationError(INCORRECT_USERNAME_EMAIL_PASSWORD)
        
        
        
# forget password / Reset password
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data["email"] = data["email"].lower()
        return data
    
    
# Password changed without old password 
class UserPasswordChangedSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(NEW_CONFIRM_PASSWORD_INCORRECT)
        
        try:
            password_reset = PasswordReset.objects.get(token=data["token"])
            self.user = password_reset.user 
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or expired token."})
        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        
        
        
#change password
class UserchangedProfilePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context.get('user')
        if not check_password(value, user.password):
            raise serializers.ValidationError(OLD_PASSWORD_INCORRECT)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(NEW_CONFIRM_PASSWORD_INCORRECT)
        return data

    def save(self):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password'])
        user.save()