from django.urls import path
from interactions import views

urlpatterns = [
    path('rating/<int:gym_id>/create', views.create_rating, name="create_rating"),
    path('rating/<int:gym_id>/<int:rating_id>/delete', views.delete_rating, name="delete_rating"),


    path('response/<int:gym_id>/<int:rating_id>/create/', views.create_response, name="create_response"),
    path('response-parent/<int:gym_id>/<int:rating_id>/response/<int:parent_id>/create/', views.create_response, name='create_response_with_parent'),
    path('response/<int:gym_id>/<int:response_id>/delete/', views.delete_response, name="delete_response"),

    # ticket validation
    path('tickets/<int:gym_id>/generate/', views.generate_ticket_temp_code, name="generate_ticket_temp_code"),
    path('tickets/<int:gym_id>/validate/', views.validate_gym_ticket, name="validate_gym_ticket"),

]
