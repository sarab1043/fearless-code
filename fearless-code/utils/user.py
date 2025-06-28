from authentication.models import User
from utils.constants import (
    SUCCESS,
    ERROR,
    DATA,
    TOKEN,
    TRUE,
    FALSE,
    USER,
    USER_NOT_FOUND,
)
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)


# Generate User Token
def generate_token(user):
    try:
        Token.objects.filter(user=user).delete()  # Delete old token
        token = Token.objects.create(user=user)
        return token
    except Exception as ex:
        None


# Login Admin User
def login_user_via_phone(phone):
    try:
        user = User.objects.filter(phone=phone).exists()
        if user:
            user = User.objects.get(phone=phone)
            token = generate_token(user)
            return {SUCCESS: TRUE, TOKEN: token.key, USER: user}
        else:
            try:
                create_user = User.objects.create(
                    phone=phone, username=phone, email=phone
                )
                token = generate_token(create_user)
                return {SUCCESS: TRUE, TOKEN: token.key, USER: create_user}
            except (AttributeError, FileNotFoundError, IntegrityError, Exception) as ex:
                # except IntegrityError as ex:
                return {SUCCESS: FALSE, ERROR: str(ex)}

    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}


# Check if user exists
def is_user_exists(key, value):
    try:
        filter = {f"{key}__exact": value}
        is_exists = User.objects.filter(**filter).exists()
        return {SUCCESS: is_exists}
    except Exception as ex:
        return {SUCCESS: FALSE}


# Check if user exists but not verified
def is_user_exists_but_not_verified(email):
    try:
        is_exists = User.objects.filter(
            Q(email=email) & Q(email_verified=False)
        ).exists()
        return {SUCCESS: is_exists}
    except Exception as ex:
        return {SUCCESS: FALSE}


# Check if user exists and verified
def is_user_exists_and_verified(email):
    try:
        is_exists = User.objects.filter(
            Q(email=email) & Q(email_verified=TRUE)
        ).exists()
        return {SUCCESS: is_exists}
    except Exception as ex:
        return {SUCCESS: FALSE}


# Get User Profile Info
def get_profile_info(request):
    try:
        user_data = {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": request.user.phone,
            "country": request.user.country,
            "image": request.user.image.url if request.user.image is not None else None,
        }
        return {SUCCESS: TRUE, DATA: user_data}
    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}


# Get All Users List
def get_users():
    try:
        users = User.objects.exclude(is_superuser=True)
        if len(users) > 0:
            return {SUCCESS: TRUE, DATA: users}
        return {SUCCESS: FALSE}
    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}


# Get User Info
def get_user(uuid):
    try:
        user = User.objects.get(uuid=uuid)
        return {SUCCESS: TRUE, DATA: user}
    except User.DoesNotExist:
        return {SUCCESS: FALSE, ERROR: USER_NOT_FOUND}

