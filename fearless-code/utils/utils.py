import random, string, logging
from django.core.mail import send_mail
from authentication.models import User
from django.utils import timezone
from datetime import timedelta
from fearless_code import settings
from utils.constants import (
    EMAIL_GENERATION_FAILED,
    EMAIL_OTP_RESEND_SUCCESS,
    EMAIL_SEND_FAILED,
    EMAIL_SENT_SUCCESS,
    MESSAGE,
    SUCCESS,
    ERROR,
    FALSE,
    TRUE
)
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import re
import uuid
import logging
import fitz
logger = logging.getLogger(__name__)


# Generate random string
def generate_random_string(length):
    try:
        letters = string.ascii_letters
        code = "".join(random.choice(letters) for i in range(length))
        return code
    except Exception as ex:
        return None
    
    
# Generate OTP
def generate_otp(length=6):
    try:
        characters = string.digits
        otp = "".join(random.choice(characters) for _ in range(length))
        print(f"otp ================ {otp}")
        return otp
    except Exception as ex:
        return None


#welcome email
def welcome_email_send(email):
    try:
        if email is not None:  
            app_url = settings.APP_URL
            user = User.objects.get(email=email)
            name = user.name.capitalize()
            context = {"name": name, 'app_url':app_url}
            subject = "Welcome"
            html_template = render_to_string("welcome-email.html", context)
            recipient_list = [email]


            email_message = EmailMessage(
                subject=subject,
                body=html_template,
                from_email=settings.SENDER_EMAIL,
                to=recipient_list,
            )
            email_message.content_subtype = "html"
            # email_message.send()
            print(f"Welcome email sent successfully to Email : {email}.")
            return {SUCCESS: TRUE, MESSAGE: EMAIL_SENT_SUCCESS}
        return {SUCCESS: FALSE, ERROR: EMAIL_GENERATION_FAILED}
    except Exception as ex:
        print(f"Email not sent successfully.Error : {str(ex)}")
        return {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED}
    
# send verification email
def send_email_verification(otp, email):
    try:
        if email is not None:  
            app_url = settings.APP_URL
            user = User.objects.get(email=email)
            name = user.name.capitalize()
            otp = otp
            context = {"name": name, "otp":otp, 'app_url':app_url}
            subject = "Email OTP"
            html_template = render_to_string("email-otp-send.html", context)
            recipient_list = [email]


            email_message = EmailMessage(
                subject=subject,
                body=html_template,
                from_email=settings.SENDER_EMAIL,
                to=recipient_list,
            )
            email_message.content_subtype = "html"
            # email_message.send()
            logger.info(f"Email sent successfully.")
            return {SUCCESS: TRUE, MESSAGE: EMAIL_SENT_SUCCESS}
        return {SUCCESS: FALSE, ERROR: EMAIL_GENERATION_FAILED}
    except Exception as ex:
        print(f"Email not sent successfully.{str(ex)}")
        return {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED}
    
    
# Send password reset token on user email
def send_password_reset_otp(email):
    try:
        app_url = settings.APP_URL
        subject = "Email OTP"
        user = User.objects.get(email=email)
        name=user.name.capitalize()
        # otp = generate_otp(6)
        otp = 111111
        user.otp = otp
        user.token_expired = timezone.now() + timedelta(minutes=1)
        user.save()
        
        context = {
            "name": name,
            "otp": otp,
            "app_url":app_url
        }
        html_template = render_to_string("email-otp-send.html", context)

        email_message = EmailMessage(
            subject=subject,
            body=html_template,
            from_email=settings.SENDER_EMAIL,
            to=[email],
        )
        
        email_message.content_subtype = "html" 
        # email_message.send() 
        logger.info(f"Resent OTP email has been sent to email")
        return {SUCCESS:TRUE, MESSAGE:EMAIL_OTP_RESEND_SUCCESS}
    except Exception as ex:
        logger.info(f"status:failed, method:send_password_reset_token, error:{str(ex)}")
        return {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED}




# format percentage value 
def formatted_value(value):
    if value % 1 == 0:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"
    
    
    
# def get_settings(key):
#     try:
#         setting = AdminSettings.objects.get(meta_key=key)
#         return setting.meta_value
#     except Exception as ex:
#         return None
    
    

def custom_send_email(subject, message, email, html_body=None):
    try:
        email_from = settings.SENDER_EMAIL
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list, html_message=html_body)
        return True
    except Exception as ex:
        logger.error(f"method: send_email(), error: {str(ex)}")



def generate_random_code_with_uuid():
    uuid_part = str(uuid.uuid4())[:8].upper()
    number_part = ''.join(random.choices(string.digits, k=4))
    code = f"{uuid_part}{number_part}"
    return code


def format_timedelta(time):
    total_seconds = int(time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def extract_data(file):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            total_pages = len(doc)
            raw_text = ""

            for index in range(10, total_pages):  # Start from page 11 (0-indexed)
                page = doc[index]
                content = page.get_text()
                # Remove embedded page number at start (like "011 ")
                content = re.sub(r"^\d{3}\s*", "", content)

                # Remove \n and \t characters from content
                content = content.replace('\n', ' ').replace('\t', ' ')

               # Replace multiple spaces with a single space
                content = re.sub(r'\s+', ' ', content).strip()
                raw_text += content

            return raw_text

    except Exception as e:
        print("❌ Error extracting PDF:", e)
        return None

# def extract_data(file):
#     try:
#         with fitz.open(stream=file.read(), filetype="pdf") as doc:
#             total_pages = len(doc)
#             pages = []

#             for index in range(10, total_pages):  # start from page 11 (0-based index)
#                 page = doc[index]
#                 content = page.get_text().strip()

#                 # Skip empty pages
#                 if not content:
#                     continue

#                 # Remove embedded page number at start (like "011 ")
#                 content = re.sub(r"^\d{3}\s*", "", content)

#                 # Remove \n and \t characters from content
#                 content = content.replace('\n', ' ').replace('\t', ' ')

#                 # Replace multiple spaces with a single space
#                 content = re.sub(r'\s+', ' ', content).strip()

#                 pages.append({
#                     "page_number": index + 1,
#                     "content": content
#                 })

#             # Remove .pdf (case insensitive) from title if present
#             title = file.name if hasattr(file, "name") else "Untitled"
#             title = re.sub(r"\.pdf$", "", title, flags=re.IGNORECASE)

#             return {
#                 "title": title,
#                 "total_pages": total_pages,
#                 "pages": pages
#             }

#     except Exception as e:
#         print("❌ Error extracting PDF:", e)
#         return None
