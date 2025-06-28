from django.urls import path
from superadmin.views import auth, languages, resources, users


urlpatterns = [
    
    path("login", auth.auth_login, name="admin-login"),
    path("logout", auth.auth_logout, name="admin-logout"),
    path("profile", auth.profile, name="profile"),
    path("dashboard", auth.admin_dashboard, name="admin-dashboard"),
    
    
    # users
    path("users", users.index, name="admin-users"),
    path("users/list", users.UsersListView.as_view(), name="admin-users-list"),
    path("users/status/<uuid:uuid>", users.status, name="admin-users-status"),
    path("users/delete/<uuid:uuid>", users.delete, name="admin-users-delete"),
    
    # resources 
    path("resources", resources.index, name="admin-resources"),
    path("resources/list", resources.ResourcesListView.as_view(), name="admin-resources-list"),
    path("resources/create", resources.create, name="admin-resources-create"),
    path("resources/edit/<uuid:uuid>", resources.edit, name="admin-resources-edit-updated"),
    path("resources/delete/<uuid:uuid>", resources.delete, name="admin-resources-delete"),
    
    #languages
    path("languages", languages.index, name="admin-languages"),
    path("languages/list", languages.LanguagesListView.as_view(), name="admin-languages-list"),
    path("languages/create", languages.create, name="admin-languages-create"),
    path("languages/edit/<uuid:uuid>", languages.edit, name="admin-languages-edit-updated"),
    path("languages/delete/<uuid:uuid>", languages.delete, name="admin-languages-delete"),
    
]
