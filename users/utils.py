from unidecode import unidecode

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from users.models import User
from crm.models import Gym

def user_is_panel_admin(user):
    return True if user.role == User.Role.ADMIN_PANEL else False

def user_is_client(user):
    return True if user.role == User.Role.CLIENT else False

def user_is_employee(user):
    return True if user.role == User.Role.EMPLOYEE else False

def panel_admin_allowed(fnc):
    @wraps(fnc)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if user_is_panel_admin(request.user):
            return fnc(request, *args, **kwargs)
        return redirect('login')

    return wrapper

def gym_employee_allowed(fnc):
    @wraps(fnc)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        gym_id = kwargs.get('gym_id')
        if not gym_id:
            return redirect('index')

        gym = Gym.objects.get(id=gym_id)
        if user_is_panel_admin(request.user):
            if request.user.adminpanelprofile.base_company != gym.base_company:
                return redirect('login')
            return fnc(request, *args, **kwargs)

        if user_is_employee(request.user):
            if gym not in request.user.employeeprofile.gyms.all():
                return redirect('login')
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

def generate_username(first_name, last_name):
    username = f"{unidecode(first_name[0])}{unidecode(last_name)}".lower()
    temp_username = username

    counter = 1
    while User.objects.filter(username=username).exists():
        if counter == 1:
            username = f"{temp_username}"
        else:
            username = f"{temp_username}{counter}"
        counter += 1

    return username
