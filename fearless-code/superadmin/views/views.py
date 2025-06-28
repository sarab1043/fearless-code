from django.shortcuts import redirect
from functools import wraps


# decorater for superuser login required
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("admin-dashboard")

    return _wrapped_view