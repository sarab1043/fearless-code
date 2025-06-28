from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from authentication.models import User
from django.contrib import messages
from utils.constants import (ACTIVE, DATA, ERROR, FALSE, INVALID_REQUEST_METHOD, MESSAGE, POST, SUCCESS, TRUE, USER_DELETED_SUCCESS, USER_NOT_FOUND, USER_STATUS_CHANGED_SUCCESS)
from django_serverside_datatable.views import ServerSideDatatableView
from superadmin.views.views import superuser_required
import logging
import re
import json
from utils.utils import generate_random_code_with_uuid
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q,  OuterRef, Subquery

logger = logging.getLogger(__name__)

# show Register user agent
@login_required(login_url='admin-login')
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/users/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/users"}
        return render(request,"500.html",context)
    
    
# Get all users using datatables
class UsersListView(ServerSideDatatableView):
    columns = [
        "uuid",
        "name",
        "email",
        "is_active",
        "date_joined"
    ]
    def get_queryset(self):
        print('enter')
        check_status = self.request.GET.get("check_status", None)
        queryset = User.objects.exclude(is_superuser=True)
        if check_status and check_status != "all-users":
            if check_status == "active":
                queryset = queryset.filter(is_active=True)
            elif check_status == "inactive":
                queryset = queryset.filter(is_active=False)
                
        return queryset
    
# Status
@login_required(login_url="admin-login")
@superuser_required
def status(request, uuid):
    try:
        if request.method == "POST":
            if uuid:
                user = User.objects.get(uuid=uuid)
                status = request.POST.get("status")
                if status == "true":
                    user.is_active = True
                    user.email_verified = True
                else:
                    user.is_active = False
                    user.email_verified = False  
                user.save()
                return JsonResponse(
                    {SUCCESS: TRUE, MESSAGE: USER_STATUS_CHANGED_SUCCESS}
                )
            return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_FOUND})
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/users"}
        return render(request,"500.html",context)
    
    
# Delete
@login_required(login_url="admin-login")
@superuser_required
def delete(request, uuid):
    try:
        if request.method == 'POST':
            user = User.objects.get(uuid=uuid)     
            user.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:USER_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})