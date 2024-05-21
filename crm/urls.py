from django.urls import path
from crm import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dashboard/', views.index, name="dashboard"),
    path('complete-infoa-bout-base-company/', views.complete_info_about_base_company, name="complete_info_about_base_company"),

    # network tab
    path('network/gyms', views.network_gyms, name="network_gyms"),
    path('network/clients', views.network_clients, name="network_clients"),

    # gym details tab
    path('gym-details/<int:gym_id>/clients/', views.gym_clients, name="gym_clients"),
    path('gym-details/<int:gym_id>/details/', views.gym_details, name="gym_details"),
    path('gym-details/<int:gym_id>/opinions/', views.gym_opinions, name="gym_opinions"),

    # clients tabs
    path('gym-list', views.clients_gyms_list, name="clients_gyms_list"),
    path('gym-details-clients/<int:gym_id>/', views.clients_gyms_details, name="clients_gyms_details"),

]
