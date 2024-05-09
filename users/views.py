from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from users.forms import LoginForm


class LoginView(LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)
