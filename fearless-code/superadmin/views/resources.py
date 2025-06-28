import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from authentication.models import User
from django.contrib import messages
from fearless_code import settings
from superadmin.forms.forms import ResourcesForm
from superadmin.models import Resources
from utils.constants import (ACTIVE, DATA, ERROR, FALSE, INVALID_FORM_DATA, INVALID_REQUEST_METHOD, MESSAGE, POST, RESOURCES_CREATED_SUCCESS, RESOURCES_DELETED_SUCCESS, RESOURCES_UPDATED_SUCCESS, SUCCESS, TRUE, USER_DELETED_SUCCESS, USER_NOT_FOUND, USER_STATUS_CHANGED_SUCCESS)
from django_serverside_datatable.views import ServerSideDatatableView
from superadmin.views.views import superuser_required
import logging
import re
import json

from utils.utils import extract_data
logger = logging.getLogger(__name__)


# show Register user agent
@login_required(login_url='admin-login')
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/resources/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/resources"}
        return render(request,"500.html",context)
 
 
class ResourcesListView(ServerSideDatatableView):
    queryset = Resources.objects.all()
    columns = [
        "uuid",
        "name",
        "type",
        "file",
        "link",
        "thumbnail",
        "created_at"
    ]      
    
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        if request.method == 'POST': 
            form = ResourcesForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                file = request.FILES.get('file') 
                extracted_data=extract_data(file)
                if extracted_data:
                    with open("fearless_code.txt", "w", encoding="utf-8") as f:
                        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
                data.save()
                messages.success(request, RESOURCES_CREATED_SUCCESS)
                return redirect('admin-resources')
            else:
                messages.error(request, INVALID_FORM_DATA)

        else:
            form = ResourcesForm()
        return render(request, 'superadmin/resources/create.html', {'form': form})

    except Exception as ex:
        messages.error(request, f"Error: {str(ex)}")
        return render(request, "500.html", {"error": str(ex), "return_url": "/admin/resources/create"})
    
    
@login_required(login_url='admin-login')
@superuser_required
def edit(request, uuid):
    try:
        resource = get_object_or_404(Resources, uuid=uuid)

        old_file_path = os.path.join(settings.MEDIA_ROOT, str(resource.file)) if resource.file else None
        old_thumbnail_path = os.path.join(settings.MEDIA_ROOT, str(resource.thumbnail)) if resource.thumbnail else None

        if request.method == "POST":
            form = ResourcesForm(request.POST, request.FILES, instance=resource)

            if form.is_valid():
                new_file = request.FILES.get('file')
                new_thumbnail = request.FILES.get('thumbnail')
                new_link = request.POST.get('link', '').strip()

                # Handle link resource
                if new_link:
                    if old_file_path and os.path.exists(old_file_path):
                        os.remove(old_file_path)
                    resource.file = None
                    resource.link = new_link
                    resource.type = "link"

                # Handle file upload
                if new_file:
                    if old_file_path and os.path.exists(old_file_path):
                        os.remove(old_file_path)
                    resource.file = new_file
                    ext = new_file.name.split('.')[-1].lower()
                    file_types = {
                        "pdf": "pdf",
                        "doc": "doc",
                        "docx": "doc",
                        "jpg": "image",
                        "jpeg": "image",
                        "png": "image",
                    }
                    resource.type = file_types.get(ext, "doc")
                    resource.link = ""

                # Handle thumbnail
                if new_thumbnail:
                    if old_thumbnail_path and os.path.exists(old_thumbnail_path):
                        os.remove(old_thumbnail_path)
                    resource.thumbnail = new_thumbnail

                resource.save()
                messages.success(request, RESOURCES_UPDATED_SUCCESS)
                return redirect('admin-resources')
            else:
                messages.error(request, INVALID_FORM_DATA)
                return render(request, 'superadmin/resources/edit.html', { "form": form })

        else:
            form = ResourcesForm(instance=resource)
            return render(request, 'superadmin/resources/edit.html', { "form": form })

    except Exception as ex:
        messages.error(request, str(ex))        
        return render(request, "500.html", {
            "error": str(ex),
            "return_url": f"/admin/resources/edit/{uuid}"
        })
    
    
@login_required(login_url="admin-login")
@superuser_required
def delete(request, uuid):
    try:
        resource = get_object_or_404(Resources, uuid=uuid)  
        if resource.file:  
            file_path = os.path.join(settings.MEDIA_ROOT, str(resource.file))
            if os.path.exists(file_path):
                os.remove(file_path)
        resource.delete()
        return JsonResponse({SUCCESS:TRUE,MESSAGE:RESOURCES_DELETED_SUCCESS, 'redirect_url':f'/admin/resources'})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})  
    