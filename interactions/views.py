from crm.models import Gym
from interactions.models import Rating, RatingResponse
from users.utils import client_allowed, gym_employee_allowed
from django.shortcuts import redirect, get_object_or_404
from django.db import IntegrityError

from django.views.decorators.http import require_POST

@require_POST
@client_allowed
def create_rating(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    try:
        Rating.objects.create(
            user=request.user,
            gym=gym,
            score=int(request.POST.get('rating')),
            comment=request.POST.get('comment')
        )
    except IntegrityError as e:
        pass

    return redirect('clients_gyms_details', gym_id=gym_id)

@require_POST
@gym_employee_allowed
def create_response(request, gym_id, rating_id, parent_id=None):
    rating = get_object_or_404(Rating, pk=rating_id)
    parent_response = get_object_or_404(RatingResponse, pk=parent_id) if parent_id else None

    comment = request.POST.get('comment')

    if comment:
        RatingResponse.objects.create(
            rating=rating,
            user=request.user,
            comment=comment,
            parent=parent_response
        )

    return redirect('gym_opinions', gym_id=gym_id)
