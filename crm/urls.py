from django.urls import path
from crm import views

urlpatterns = [
    path('', views.index, name="index"),

    path('complete-infoa-bout-base-company/', views.complete_info_about_base_company,
         name="complete_info_about_base_company"),
    # dashboard
    path('dashboard/', views.index, name="dashboard"),
    path('dashboard/<int:gym_id>/get_data/', views.get_dashboard_data, name="get_dashboard_data"),

    # network tab
    path('network/gyms', views.network_gyms, name="network_gyms"),
    path('network/clients', views.network_clients, name="network_clients"),

    # gym details tab
    path('gym-details/<int:gym_id>/assortment/', views.gym_assortment, name="gym_assortment"),
    path('gym-details/<int:gym_id>/services/', views.gym_service, name="gym_service"),
    path('gym-details/<int:gym_id>/clients/', views.gym_clients, name="gym_clients"),
    path('gym-details/<int:gym_id>/campaigns/', views.gym_campaigns, name="gym_campaigns"),
    path('gym-details/<int:gym_id>/client-details/<int:client_id>', views.client_details, name="client_details"),


    path('gym-details/<int:gym_id>/details/', views.gym_details, name="gym_details"),
    path('gym-details/<int:gym_id>/opinions/', views.gym_opinions, name="gym_opinions"),
    path('gym-details/<int:gym_id>/tickets/', views.gym_tickets, name="gym_tickets"),
    path('gym-details/<int:gym_id>/tickets/create/', views.buy_gym_ticket_as_emp, name="buy_gym_ticket_as_emp"),

    # clients tabs
    path('gym-list', views.clients_gyms_list, name="clients_gyms_list"),
    path('gym-details-clients/<int:gym_id>/', views.clients_gyms_details, name="clients_gyms_details"),

    path('gym-tickets/', views.clients_gyms_tickets, name="clients_gyms_tickets"),
    path('buy-gym_ticket/', views.buy_gym_ticket_as_client, name="buy_gym_ticket_as_client"),

]
