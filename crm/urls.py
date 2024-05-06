from django.urls import path
from crm import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('dashboard/', views.dashboard, name="dashboard"),
]
