from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from users.forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from users.models import UserFactory, User
from django.contrib.auth import logout

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
