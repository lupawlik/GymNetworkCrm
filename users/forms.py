from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from users.models import User


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        required=True
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        required=True
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "Password"}),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "Confirm Password"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            "placeholder": "Email",
        }),
        required=True
    )
    panel_admin_account = forms.BooleanField(
        label=_("Create account for gym network owner:"),
        widget=forms.CheckboxInput(attrs={}),
        required=False

    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder": "Username",
                "autocomplete": "off",
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                "placeholder": "Email",
                "autocomplete": "off",
            })
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Old Password"
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "New Password"
    }), label="New Password")
    new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Confirm Password"
    }), label="Confirm New Password")
