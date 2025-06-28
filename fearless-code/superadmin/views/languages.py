import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from authentication.models import Language, User
from django.contrib import messages
from fearless_code import settings
from superadmin.forms.forms import LanguagesForm
from utils.constants import (ACTIVE, DATA, ERROR, FALSE, INVALID_FORM_DATA, INVALID_REQUEST_METHOD, LANGUAGE_CREATED_SUCCESS, LANGUAGE_DELETED_SUCCESS, LANGUAGE_UPDATED_SUCCESS, MESSAGE, POST, SUCCESS, TRUE, USER_DELETED_SUCCESS, USER_NOT_FOUND, USER_STATUS_CHANGED_SUCCESS)
from django_serverside_datatable.views import ServerSideDatatableView
from superadmin.views.views import superuser_required
import logging
import re
import json
logger = logging.getLogger(__name__)


# show Register user agent
@login_required(login_url='admin-login')
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/languages/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/languages"}
        return render(request,"500.html",context)
 
 
class LanguagesListView(ServerSideDatatableView):
    queryset = Language.objects.all()
    columns = [
        "uuid",
        "code",
        "name",
    ]      
    
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        if request.method == 'POST': 
            form = LanguagesForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, LANGUAGE_CREATED_SUCCESS)
                return redirect('admin-languages')
            else:
                messages.error(request, INVALID_FORM_DATA)

        else:
            form = LanguagesForm()
        return render(request, 'superadmin/languages/create.html', {'form': form})

    except Exception as ex:
        messages.error(request, f"Error: {str(ex)}")
        return render(request, "500.html", {"error": str(ex), "return_url": "/admin/languages/create"})
    
    
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        language = get_object_or_404(Language, uuid=uuid)
        if request.method == "POST":
            form = LanguagesForm(request.POST, instance=language)

            if form.is_valid():
                form.save() 
                messages.success(request, LANGUAGE_UPDATED_SUCCESS)
                return redirect('admin-languages')

            else:
                context = { "form": form }
                messages.error(request, INVALID_FORM_DATA)
                return render(request, 'superadmin/languages/edit.html', context)

        form = LanguagesForm(instance=language)
        context = { "form": form }
        return render(request, 'superadmin/languages/edit.html', context)

    except Exception as ex:
        messages.error(request, str(ex))        
        context = { ERROR: str(ex), "return_url": f"/admin/languages/edit/{uuid}" }
        return render(request, "500.html", context)
    
    
@login_required(login_url="admin-login")
@superuser_required
def delete(request, uuid):
    try:
        language = get_object_or_404(Language, uuid=uuid)  
        language.delete()
        return JsonResponse({SUCCESS:TRUE,MESSAGE:LANGUAGE_DELETED_SUCCESS})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})  
    