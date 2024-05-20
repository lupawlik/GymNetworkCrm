from django.urls import path
from users import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('change-password/', views.ChangePasswordView.as_view(), name="change_password"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_user, name="logout"),

    path('employees/', views.network_employees, name="network_employees"),
]
