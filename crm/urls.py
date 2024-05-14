from django.urls import path
from crm import views

urlpatterns = [
    path('', views.dashboard, name="index"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('complete-infoa-bout-base-company/', views.complete_info_about_base_company, name="complete_info_about_base_company"),
]
