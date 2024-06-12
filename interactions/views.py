from random import randrange
from crm.models import Gym
from interactions.models import Rating, RatingResponse, TicketTempCode, NewsletterAgree, PromotionsAgree, PushNotification
from django.http import JsonResponse
from users.utils import client_allowed
from users.models import Ticket, TicketEntrance
from django.shortcuts import redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from django.views.decorators.http import require_POST
from users.utils import user_is_employee, user_is_panel_admin, gym_employee_allowed


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
@client_allowed
def delete_rating(request, gym_id, rating_id):
    rating = Rating.objects.get(id=rating_id)

    if request.user == rating.user:
        rating.delete()

    return redirect('clients_gyms_details', gym_id=gym_id)


@require_POST
@login_required(login_url='login')
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

    if user_is_employee(request.user) or user_is_panel_admin(request.user):
        return redirect('gym_opinions', gym_id=gym_id)

    return redirect('clients_gyms_details', gym_id=gym_id)


@require_POST
@login_required(login_url='login')
def delete_response(request, gym_id, response_id):
    response = RatingResponse.objects.get(id=response_id)

    if request.user == response.user:
        response.delete()

    if user_is_employee(request.user) or user_is_panel_admin(request.user):
        return redirect('gym_opinions', gym_id=gym_id)

    return redirect('clients_gyms_details', gym_id=gym_id)


@require_POST
@login_required(login_url='login')
def generate_ticket_temp_code(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    ticket = TicketTempCode.objects.create(
        user=request.user,
        gym=gym,
        ticket_id=int(request.POST.get('ticket_id'))
    )

    return JsonResponse({'code': ticket.code})


@require_POST
@gym_employee_allowed
def validate_gym_ticket(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    try:
        code = TicketTempCode.objects.filter(
            code=request.POST.get('code'),
            gym=gym,
        )[:1].get()
    except ObjectDoesNotExist:
        return JsonResponse({'text_response': 'Invalid code!'})

    if not code.is_valid():
        return JsonResponse({'text_response': 'Code expired!'})

    ticket_to_check = code.ticket_id

    try:
        ticket = Ticket.objects.get(id=ticket_to_check)
    except ObjectDoesNotExist:
        return JsonResponse({'text_response': 'This customer does not have a ticket to this gym!'})

    if not ticket.is_valid():
        return JsonResponse({'text_response': 'This ticket expired!'})

    TicketEntrance.objects.create(
        ticket=ticket
    )

    return JsonResponse({'text_response': f'Valid ticket! Until: {ticket.valid_until}'})


@require_POST
@client_allowed
def change_promotion_agree(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    status = True if request.POST.get('status') == 'true' else False

    if status:
        PromotionsAgree.objects.get_or_create(
            gym=gym,
            user=request.user
        )
    else:
        PromotionsAgree.objects.get(
            gym=gym,
            user=request.user
        ).delete()

    return JsonResponse({'ok': 200})


@require_POST
@client_allowed
def change_newsletter_agree(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    status = True if request.POST.get('status') == 'true' else False

    if status:
        NewsletterAgree.objects.get_or_create(
            gym=gym,
            user=request.user
        )
    else:
        NewsletterAgree.objects.get(
            gym=gym,
            user=request.user
        ).delete()

    return JsonResponse({'ok': 200})

@require_POST
@gym_employee_allowed
def export_users_agreement(request, gym_id):
    gym = Gym.objects.get(id=gym_id)
    export_type = request.POST.get('type')

    if export_type == 'newsletter':
        users = NewsletterAgree.objects.filter(gym=gym)
    elif export_type == 'promotion':
        users = PromotionsAgree.objects.filter(gym=gym)
    else:
        return JsonResponse({'error': 'Invalid export type'}, status=400)

    user_data = "\n".join([f"{user.user.username} ({user.user.email})" for user in users])
    return JsonResponse({'users': user_data})

@require_POST
@client_allowed
def mark_push_as_read(request, push_id):
    push = PushNotification.objects.get(id=push_id)

    if push.user != request.user:
        return JsonResponse({'msg': 'You dont have access'}, status=403)

    push.is_opened = True
    push.opened_at = timezone.now()
    push.save()

    return JsonResponse({'msg': 'ok'}, status=200)
