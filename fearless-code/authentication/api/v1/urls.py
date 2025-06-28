from django.urls import path
from authentication.api.v1 import views



urlpatterns = [
    path("auth/login", views.UserLoginAPIView.as_view(), name="login"),
    path("auth/register", views.UserRegistrationView.as_view(), name="auth-register"),
    path("auth/verify-otp", views.UserVerificationView.as_view(), name="verify-otp"),
    path("auth/resend-otp", views.ResendVerificationView.as_view(), name="resend-otp"),
    path("auth/forget-password", views.ForgetResetRequestView.as_view(),name="forget-password"),
    path("auth/reset-verify-otp", views.ResetPasswordVerifyOTPView.as_view(), name="reset-verify-otp"),
    path("auth/reset-password", views.PasswordResetRequestView.as_view(),name="forget-password"),
    path("auth/logout", views.LogoutAPIView.as_view(), name="logout"),
    
    #manage user profile
    path('manage-profile', views.UserManageProfileApiView.as_view(), name="user-manage-profile"),  
    # user profile change password
    path('change-password', views.UserProfileChangePasswordApiView.as_view(), name="user-manage-profile"), 
    
]
