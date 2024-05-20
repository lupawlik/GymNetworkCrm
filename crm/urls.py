from django.urls import path
from crm import views

urlpatterns = [
    path('', views.dashboard, name="index"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('complete-infoa-bout-base-company/', views.complete_info_about_base_company, name="complete_info_about_base_company"),

    # network tab
    path('network/gyms', views.network_gyms, name="network_gyms"),
    path('network/clients', views.network_clients, name="network_clients"),

    # gym details tab
    path('gym-details/<int:gym_id>/clients/', views.gym_clients, name="gym_clients"),
]
