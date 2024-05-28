from PIL import Image
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Case, When, BooleanField
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from users.utils import panel_admin_allowed, gym_employee_allowed, user_is_client, client_allowed
from crm.models import BaseCompany, BaseCompanyAddress, Gym, GymAddress, GymPricing
from users.models import Ticket, Client
from django.core.exceptions import ObjectDoesNotExist
from interactions.models import NewsletterAgree, PromotionsAgree


def index(request):
    context = {
        'segment': 'dashboard',
    }

    if not request.user.is_authenticated:
        return redirect('login')

    if user_is_client(request.user):
        return redirect('clients_gyms_list')

    return render(request, 'crm/dashboard.html', context)


@panel_admin_allowed
def complete_info_about_base_company(request):
    context = {}

    if request.user.adminpanelprofile.base_company:
        return redirect('index')

    if request.method == "POST":
        company_address = BaseCompanyAddress.objects.create(
            address_l1=request.POST.get('address_l1'),
            address_l2=request.POST.get('address_l2'),
            city=request.POST.get('city'),
            zip_code=request.POST.get('zip_code'),
            country=request.POST.get('country'),
            email_address=request.POST.get('email'),
            phone_nr=request.POST.get('phone_nr'),
        )

        company = BaseCompany.objects.create(
            vat_id=request.POST.get('vat_id'),
            company_name=request.POST.get('company_name'),
            address=company_address,
        )

        request.user.adminpanelprofile.base_company = company
        request.user.adminpanelprofile.save()

        return redirect('index')

    return render(request, 'crm/complete_info_about_base_company.html', context)


@panel_admin_allowed
def network_gyms(request):
    context = {
        'parent': 'network',
        'segment': 'gyms',
        'all_gyms': Gym.objects.filter(base_company=request.user.adminpanelprofile.base_company)
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'add_gym':
            gym_address = GymAddress.objects.create(
                address_l1=request.POST.get('address_l1'),
                address_l2=request.POST.get('address_l2'),
                city=request.POST.get('city'),
                zip_code=request.POST.get('zip_code'),
                country=request.POST.get('country'),
                email_address=request.POST.get('email'),
                phone_nr=request.POST.get('phone_nr'),
            )

            Gym.objects.create(
                name=request.POST.get('gym_name'),
                base_company=request.user.adminpanelprofile.base_company,
                address=gym_address,
            )

            return redirect('network_gyms')

    return render(request, 'crm/network_gyms.html', context)


@panel_admin_allowed
def network_clients(request):
    context = {
        'parent': 'network',
        'segment': 'clients',
    }

    return render(request, 'crm/network_clients.html', context)


@gym_employee_allowed
def gym_clients(request, gym_id):
    gym = Gym.objects.get(id=gym_id)
    tickets = Ticket.objects.filter(gym=gym).select_related('user')
    status_filter = request.GET.get('status', 'all')

    clients = {}
    for ticket in tickets:
        if ticket.user not in clients:
            clients[ticket.user] = ticket.is_valid()

    if status_filter == 'active':
        clients = {user: is_valid for user, is_valid in clients.items() if is_valid}
    elif status_filter == 'inactive':
        clients = {user: is_valid for user, is_valid in clients.items() if not is_valid}

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_clients',
        'clients': clients,
        'status_filter': status_filter,
    }

    return render(request, 'crm/network_clients.html', context)


@gym_employee_allowed
def gym_details(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_details',
        'gym': gym,
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'edit_gym_info':
            gym.name = request.POST.get('name')
            gym.description = request.POST.get('description')

            gym.opening_time_to = request.POST.get('opening_hours_to') if request.POST.get('opening_hours_to') else None
            gym.opening_time_from = request.POST.get('opening_hours_from') if request.POST.get(
                'opening_hours_from') else None

            photo = request.FILES.get('image')
            if photo:
                try:
                    image = Image.open(photo)
                except IOError:
                    return JsonResponse({'error': 'Unable to open image'}, status=400)

                png_buffer = BytesIO()
                image.save(png_buffer, format='PNG')
                png_buffer.seek(0)

                gym.image.save(f'gym_{gym.id}_{uuid4()}.png', png_buffer)

            gym.address.address_l1 = request.POST.get('address_l1')
            gym.address.address_l2 = request.POST.get('address_l2')
            gym.address.city = request.POST.get('city')
            gym.address.zip_code = request.POST.get('zip_code')
            gym.address.country = request.POST.get('country')
            gym.address.email_address = request.POST.get('email')
            gym.address.phone_nr = request.POST.get('phone_nr')

            gym.address.save()
            gym.save()

        if request.POST.get('action') == 'add_pricing':
            GymPricing.objects.create(
                gym=gym,
                name=request.POST.get('name'),
                price=request.POST.get('price'),
            )

        if request.POST.get('action') == 'delete_pricing':
            GymPricing.objects.get(id=request.POST.get('id_to_remove')).delete()

        return redirect('gym_details', gym_id=gym_id)

    return render(request, 'crm/gyms/gym_details.html', context)


@gym_employee_allowed
def gym_opinions(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_opinions',
        'gym': gym,
        'ratings': gym.ratings.order_by('-created_at')
    }

    return render(request, 'crm/gyms/gym_opinions.html', context)


@gym_employee_allowed
def gym_tickets(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'gym': gym,
        'segment': 'gym_tickets',
        'tickets': Ticket.objects.filter(gym=gym).annotate(
            is_active=Case(
                When(valid_until__gt=timezone.now(), then=True),
                default=False,
                output_field=BooleanField()
            )
        ).order_by('-is_active', 'valid_until'),
    }

    return render(request, 'crm/gyms/gym_tickets.html', context)

@require_POST
@gym_employee_allowed
def buy_gym_ticket_as_emp(request, gym_id):
    gym = Gym.objects.get(id=gym_id)
    ticket_type = GymPricing.objects.get(gym=gym, name=request.POST.get('ticket_type'))
    price = ticket_type.price * int(
        request.POST.get('duration'))
    ticket_until = datetime.now() + relativedelta(months=int(request.POST.get('duration')))

    try:
        user = Client.objects.get(username=request.POST.get('username'))
    except ObjectDoesNotExist:
        return redirect('gym_tickets', gym_id=gym.id)

    Ticket.objects.create(
        user=user,
        gym=gym,
        price=price,
        valid_until=ticket_until,
        ticket_type=ticket_type.name
    )

    return redirect('gym_tickets', gym_id=gym.id)


# clients views
@client_allowed
def clients_gyms_list(request):
    context = {
        'segment': 'clients_gym_list',
        'gyms': Gym.objects.all()
    }
    return render(request, 'crm/clients_side/gyms_list.html', context)


@client_allowed
def clients_gyms_details(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'segment': 'clients_gym_list',
        'gym': gym,
        'ratings': gym.ratings.order_by('-created_at'),
        'promotions': True if PromotionsAgree.objects.filter(gym=gym, user=request.user) else False,
        'newsletter': True if NewsletterAgree.objects.filter(gym=gym, user=request.user) else False,
    }
    return render(request, 'crm/clients_side/gym_details_clients.html', context)


@client_allowed
def clients_gyms_tickets(request):
    context = {
        'segment': 'clients_gym_ticket',
        'tickets': Ticket.objects.filter(user=request.user).annotate(
            is_active=Case(
                When(valid_until__gt=timezone.now(), then=True),
                default=False,
                output_field=BooleanField()
            )
        ).order_by('-is_active', 'valid_until'),
    }

    return render(request, 'crm/clients_side/gym_tickets_clients.html', context)


@client_allowed
@require_POST
def buy_gym_ticket_as_client(request):
    gym = Gym.objects.get(id=request.POST.get('gym_id'))
    ticket_type = GymPricing.objects.get(gym=gym, name=request.POST.get('ticket_type'))
    price = ticket_type.price * int(
        request.POST.get('duration'))
    ticket_until = datetime.now() + relativedelta(months=int(request.POST.get('duration')))

    Ticket.objects.create(
        user=request.user,
        gym=gym,
        price=price,
        valid_until=ticket_until,
        ticket_type=ticket_type.name
    )

    return redirect('clients_gyms_details', gym_id=gym.id)
