from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import User
from django.contrib import messages
from superadmin.views.views import superuser_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from utils.constants import (    
    ACCESS_RESTRICTON,
    ERROR,
    FALSE,
    INVALID_LOGIN_DETAILS,
    INVALID_OLD_PASSWORD,
    INVALID_PASSWORD,
    LOGIN_ACCOUNT,
    LOGIN_SUCCESS,
    LOGOUT_SUCCESS,
    PROFILE_UPDATED_SUCCESS,
    SUCCESS,
    TRUE,
    MESSAGE,
    USER_NOT_ACTIVE,
    USER_NOT_FOUND, 
)
from django.db.models import Sum, Q
import logging
logger = logging.getLogger(__name__)


def auth_login(request):
    try:        
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            try:
                user = User.objects.get(Q(email=email))
            except User.DoesNotExist:
                return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_FOUND})
            
            if user.is_active:
                user = authenticate(email=email, password=password)
                if user is not None:
                    # Check if user is a superuser
                    if user.is_superuser:
                        login(request, user)
                        messages.success(request, LOGIN_SUCCESS)
                        return JsonResponse({SUCCESS: TRUE, MESSAGE: LOGIN_SUCCESS})
                    else:
                        return JsonResponse(
                            {SUCCESS: FALSE, ERROR: ACCESS_RESTRICTON}
                        )
                else:
                    return JsonResponse(
                        {SUCCESS: FALSE, ERROR: INVALID_LOGIN_DETAILS}
                    )
            return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_ACTIVE})
        else:
            if request.user.is_authenticated and request.user.is_superuser:
                return redirect("admin-dashboard")
            elif request.user.is_authenticated:
                return redirect("admin-dashboard")
            else:
                return render(request, "login.html")
    except Exception as ex:
        return JsonResponse({SUCCESS: FALSE, ERROR: f"Error: {str(ex)}"})
    
    
# profile
@login_required(login_url="login")
def profile(request):
    try:
        if request.method == "POST" and request.POST.get('type') == "update_info":
            try:
                name = request.POST.get("name")  
                user = request.user
                user.name = name
                user.save()
                messages.success(request, PROFILE_UPDATED_SUCCESS)
                return redirect("profile")

            except Exception as ex:
                messages.error(request, str(ex))        
                context = {ERROR:str(ex),"return_url":"/profile"}
                return render(request,"500.html",context)

        elif request.method == "POST" and request.POST.get('type') == "update_password":
            try:
                current_password = request.POST.get("current_password")
                if check_password(current_password, request.user.password):
                    password = request.POST.get("password")
                    if password:
                        user = request.user
                        user.set_password(password)
                        user.save()
                        login(request, user)
                        messages.success(request, PROFILE_UPDATED_SUCCESS)
                        return redirect("profile")
                    messages.error(request, INVALID_PASSWORD)
                    return redirect("profile")
                messages.error(request, INVALID_OLD_PASSWORD)
                return redirect("profile")
            except Exception as ex:
                messages.error(request, str(ex))        
                context = {ERROR:str(ex),"return_url":"/profile"}
                return render(request,"500.html",context)

        if request.user.is_authenticated:
            return render(request,"profile.html")
        else:
            messages.error(request, LOGIN_ACCOUNT)  
            return redirect("admin-login")
    except Exception as ex:
        messages.error(request, str(ex))        
        context = {ERROR:str(ex),"return_url":"/profile"}
        return render(request,"500.html",context)
    
    
# Logout User
@login_required(login_url="login")
def auth_logout(request):
    try:
        logout(request)
        messages.success(request, LOGOUT_SUCCESS)
        return redirect("admin-login")
    except Exception as ex:
        messages.error(request, str(ex))        
        context = {ERROR:str(ex),"return_url":"/profile"}
        return render(request,"500.html",context)
    
    
    
# Admin Dashboard
@login_required(login_url="admin-login")
def admin_dashboard(request):
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            users = User.objects.exclude(is_superuser=True).count()
            return render(request, "superadmin/dashboard.html",{
                    "users": users,   
                },
            )
        else:
            print('enter')
            return redirect("admin-login")
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/dashboard"}
        return render(request,"500.html",context)
    
    
