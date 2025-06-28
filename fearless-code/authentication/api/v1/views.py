from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework import generics
from authentication.serializers import LoginSerializer, PasswordResetSerializer, UserPasswordChangedSerializer, UserRegistrationSerializer, UserSerializer, UserchangedProfilePasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from authentication.models import User, PasswordReset, Language
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from utils.constants import *
from utils.validators import format_validation_errors
from utils.user import (
    generate_token,
    is_user_exists_and_verified,
    is_user_exists_but_not_verified,
)
from utils.utils import *
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication   
import uuid
import logging
logger = logging.getLogger(__name__)



#register 
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        try:
            response = {}
            serializer = self.get_serializer(data=request.data)
            is_exists = is_user_exists_but_not_verified(request.data["email"].lower())
            
            if is_exists[SUCCESS]:
                user = User.objects.get(email=request.data["email"].lower())
                if user.token_expired and timezone.now() < user.token_expired:
                        return Response(
                            {
                                SUCCESS: FALSE,
                                ERROR: EMAIL_ALREADY_SENT,
                                IS_VERIFIED: FALSE,
                                TOKEN:user.device_token
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )
                # otp = generate_otp(6)
                otp = 111111
                
                is_sent = send_email_verification(otp, request.data["email"].lower())
                if is_sent[SUCCESS]:
                    token = generate_token(user)
                    user.otp=otp
                    user.device_token = token.key
                    user.token_expired = timezone.now() + timedelta(minutes=1)
                    user.save()
                    
                    return Response(
                        {SUCCESS: TRUE, MESSAGE: EMAIL_SEND_SUCCESS, IS_VERIFIED: FALSE, TOKEN:token.key},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            # If user exists and verified
            is_exists = is_user_exists_and_verified(request.data["email"].lower())
            if is_exists[SUCCESS]:
                return Response(
                    {
                        SUCCESS: FALSE,
                        ERROR: REGISTER_EMAIL_ALREADY_EXISTS,
                        IS_LOGIN: TRUE,
                        IS_VERIFIED: TRUE,
                    },
                    status=status.HTTP_200_OK,
                )
            # If user do not exists
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                # otp = generate_otp(6)
                otp = 111111
                token = generate_token(user)
                user.device_token = token.key
                user.token_expired = timezone.now() + timedelta(minutes=1)
                user.otp = otp
                
                #default lang
                default_language = Language.objects.filter(code='en').first()
                user.language = default_language
                user.save()
                is_sent = send_email_verification(otp, serializer.data["email"])
                
                if is_sent[SUCCESS]:
                    return Response(
                        {
                            SUCCESS: TRUE, 
                            MESSAGE: EMAIL_SEND_SUCCESS, 
                            TOKEN:token.key
                        },
                        status=status.HTTP_200_OK,
                    )
                logger.info(f"Otp not sent to email: {serializer.data['email']}")
                return Response(
                    {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED},
                    status=status.HTTP_404_NOT_FOUND,
                )

            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
            
# user verification view
class UserVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            token = request.data.get('token')
            otp = request.data.get('otp')
            try:
                user = User.objects.filter(device_token=token, otp=otp).first()
            except User.DoesNotExist:
                return Response(
                    {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            if not user:
                return Response(
                    {SUCCESS: FALSE, ERROR: INVALID_OTP},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            if timezone.now() > user.token_expired:
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_EXPIRED},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            if user.is_active == TRUE and user.email_verified == TRUE:
                return Response(
                    {SUCCESS: TRUE, MESSAGE: EMAIL_ALREADY_VERIFIED_SUCCESS},
                    status=status.HTTP_404_NOT_FOUND,
                )
                

            user.email_verified = True
            user.is_active = True
            user.otp = None
            user.device_token = None
            user.save()
            token = generate_token(user)
            email = user.email
            is_sent = welcome_email_send(email)
            if is_sent[SUCCESS]:
                logger.info(f"Welcome email send successfully to {email}")
            else:
                logger.error(f"Welcome email not send to {email}")
            serializer = UserSerializer(user)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: USER_CREATED_SUCCESS, 
                    TOKEN: token.key,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
            
            
# resend otp email
class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            token = request.data.get('token')
            
            try:
                user = User.objects.get(device_token=token)
            except User.DoesNotExist:
                return Response(
                    {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            token = generate_token(user)
            email = user.email
            # otp = generate_otp(6)
            otp = 111111
            user.otp = otp
            user.device_token = token.key
            user.token_expired = timezone.now() + timedelta(minutes=1)
            user.save()
            is_sent = send_email_verification(otp, email)
            if is_sent[SUCCESS]:
                return Response(
                    {SUCCESS: TRUE, MESSAGE: EMAIL_SEND_SUCCESS, TOKEN:token.key},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {SUCCESS: FALSE, ERROR: EMAIL_SEND_FAILED},
                status=status.HTTP_404_NOT_FOUND,
            )
          
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
       
#login      
class UserLoginAPIView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})            
            if serializer.is_valid():                
                serializer.is_valid(raise_exception=True)
                validated_data = serializer.validated_data
                user = validated_data.get("user")                
                token = generate_token(user)                
                user_serializer = UserSerializer(user, context={'user': user, 'request':request})
                user_data = user_serializer.data 

                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: LOGIN_SUCCESS,
                        TOKEN: token.key,
                        DATA: user_data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: INVALID_LOGIN_CREDENTIALS,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )



# Forget Reset View
class ForgetResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetSerializer

    def create(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                user = get_user_model().objects.filter(email=email).first()
              
                if user:
                    if not user.is_active:
                        return Response(
                        {SUCCESS: FALSE, ERROR: VERIFY_ACCOUNT_EMAIL_ADDRESS},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if user:
                    # Generate a unique token
                    token = uuid.uuid4()

                    # Create a Password Reset token
                    password_reset, created = PasswordReset.objects.update_or_create(
                            user=user, defaults={"token": token}
                        )
                    is_sent = send_password_reset_otp(email)
                    if is_sent[SUCCESS]:
                        logger.info(f"Email OTP resent to email : {email}")
                        return Response(
                            {SUCCESS: TRUE, MESSAGE: PASSWORD_CODE_SEND_SUCCESS, TOKEN :password_reset.token},
                            status=status.HTTP_200_OK,
                        )
                    return Response(
                        {SUCCESS: FALSE, ERROR: TOKEN_SEND_EMAIL_FAILED},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                else:
                    return Response(
                        {SUCCESS: FALSE, ERROR: EMAIL_DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: INVALID_EMAIL,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
# Resent otp verify for password
class ResetPasswordVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            token = request.data.get('token')
            otp = request.data.get('otp')
            
            try:
                password_token = PasswordReset.objects.get(token=token, user__otp=otp)
            except PasswordReset.DoesNotExist:
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_NOT_VALID},
                    status=status.HTTP_404_NOT_FOUND,
                )
        
            user = password_token.user
            if timezone.now() > user.token_expired:
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_EXPIRED},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            user.otp = None
            user.save()
            
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: USER_VERIFICATION_SUCCESS,
                    TOKEN: token,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
                 
#password reset
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def put(self, request):
        try:
           
            serializer = UserPasswordChangedSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: PASSWORD_CHANGED_SUCCESS,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                
                error_message = format_validation_errors(serializer)
                return Response(
                    {
                        SUCCESS: FALSE,
                        ERROR: error_message
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as ex:
            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: str(ex)
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
            

# Logout
class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.auth.delete()
            return Response(
                {SUCCESS: TRUE, MESSAGE: LOGOUT_SUCCESSFULLY}, status=status.HTTP_200_OK
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
        


# user manage profile    
class UserManageProfileApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user 
            serializer = UserSerializer(user,context={'user': user, 'request': request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: PROFILE_DATA_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
     # update the tracked category  
    def put(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True,  context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: PROFILE_UPDATED_SUCCESS,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        SUCCESS: FALSE,
                        ERROR: PROFILE_NOT_UPDATED
                       
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
                
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
    def delete(self, request):
        try:
            user = request.user 
            user.delete()
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: PROFILE_DELETED_SUCCESS,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        
        
# user profile change password     
class UserProfileChangePasswordApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def put(self, request, *args, **kwargs):
            try:
                user = request.user
                serializer = UserchangedProfilePasswordSerializer(data=request.data, context={'user': user})

                if serializer.is_valid():
                    serializer.save()
                    
                    return Response(
                        {
                            SUCCESS: TRUE,
                            MESSAGE: PASSWORD_CHANGED_SUCCESS
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    
                    error_message = format_validation_errors(serializer)
                    return Response(
                        {
                            SUCCESS: FALSE,
                            ERROR: error_message
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

            except Exception as ex:
                return Response({SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND)