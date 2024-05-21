from django.urls import path
from interactions import views

urlpatterns = [
    path('interactions/<int:gym_id>', views.create_rating, name="create_rating"),
    path('interactions/<int:gym_id>/<int:rating_id>', views.create_response, name="create_response"),
    path('interactions/<int:gym_id>/<int:rating_id>/response/<int:parent_id>/', views.create_response, name='create_response_with_parent'),

]
