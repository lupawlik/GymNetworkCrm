import json

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from users.forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from users.models import UserFactory, User
from django.contrib.auth import logout
from django.db.models import Q
from django.contrib import messages

from crm.models import Gym
from users.utils import panel_admin_allowed, generate_username
class LoginView(LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            admin_panel_account = form.cleaned_data.get('panel_admin_account')
            account_type = User.Role.ADMIN_PANEL if admin_panel_account else User.Role.CLIENT

            UserFactory.create_user(
                user_type=account_type,
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password1'])
            )

            return redirect(reverse_lazy('login'))
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')

@panel_admin_allowed
def network_employees(request):
    all_gyms = [{'id': gym.id, 'name': gym.name} for gym in Gym.objects.filter(base_company=request.user.adminpanelprofile.base_company)]
    context = {
        'parent': 'network',
        'segment': 'employees',
        'all_gyms': json.dumps(all_gyms),
        'all_employees': User.objects.filter(Q(role=User.Role.ADMIN_PANEL) | Q(role=User.Role.EMPLOYEE)),
        'employees_roles': [User.Role.ADMIN_PANEL, User.Role.EMPLOYEE]

    }

    if request.method == 'POST':
        if request.POST.get('action') == 'add_employee':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            username = generate_username(first_name, last_name)
            email = request.POST.get('email')
            password = User.objects.make_random_password()

            if request.POST.get('role') == 'ADMIN_PANEL':
                user = UserFactory.create_user(
                    user_type=User.Role.ADMIN_PANEL,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password)
                )

                user.adminpanelprofile.base_company = request.user.adminpanelprofile.base_company
                user.adminpanelprofile.save()
                messages.success(request, f"Admin added. Temp password for {username} is: {password}")

            if request.POST.get('role') == 'EMPLOYEE':
                gyms = Gym.objects.filter(id__in=request.POST.getlist('gyms[]'), base_company=request.user.adminpanelprofile.base_company)

                user = UserFactory.create_user(
                    user_type=User.Role.EMPLOYEE,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password)
                )

                user.employeeprofile.base_company = request.user.adminpanelprofile.base_company

                user.employeeprofile.salary = float(request.POST.get('salary'))
                user.employeeprofile.gyms.add(*gyms)

                user.employeeprofile.save()

                messages.success(request, f"Employee added. Temp password for {username} is: {password}")

            return redirect('network_employees')

    return render(request, 'users/network_employees.html', context)