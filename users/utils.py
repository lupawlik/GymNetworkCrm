from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from users.models import User

def user_is_panel_admin(user):
    return True if user.role == User.Role.ADMIN_PANEL else False

def user_is_client(user):
    return True if user.role == User.Role.CLIENT else False

def panel_admin_allowed(fnc):
    @wraps(fnc)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if user_is_panel_admin(request.user):
            return fnc(request, *args, **kwargs)
        return redirect('login')

    return wrapper


def client_allowed(fnc):
    @wraps(fnc)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if user_is_client(request.user):
            return fnc(request, *args, **kwargs)
        return redirect('login')

    return wrapper
