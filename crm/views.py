import calendar
from PIL import Image
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Case, When, BooleanField, Sum, Min
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from users.utils import panel_admin_allowed, gym_employee_allowed, user_is_client, user_is_panel_admin, \
    user_is_employee, client_allowed, check_if_client_is_connected_with_gym
from crm.models import BaseCompany, BaseCompanyAddress, Gym, GymAddress, GymPricing, Assortment, Services
from users.models import Ticket, Client, TicketEntrance
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

    if request.user.is_superuser:
        return redirect('/admin/')

    if user_is_employee(request.user):
        gyms = request.user.employeeprofile.gyms.all()
    elif user_is_panel_admin(request.user):
        gyms = request.user.adminpanelprofile.base_company.gyms.all()

    context['gyms'] = gyms
    context['current_year'] = timezone.now().year

    return render(request, 'crm/dashboard.html', context)


@gym_employee_allowed
def get_dashboard_data(request, gym_id):
    year = int(request.POST.get('year', timezone.now().year))

    if gym_id:
        gym = Gym.objects.get(id=gym_id)
        data = {
            'labels': [calendar.month_name[i] for i in range(1, 13)],
            'active_tickets': [],
            'purchased_tickets': [],
            'tickets_usage': [],
            'avg_ticket_price_for_new_client': [],
            'new_clients': [],
            'earnings': [],
            'promotions_agree': [],
            'newsletter_agree': []
        }

        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1])

            active_tickets_count = Ticket.objects.filter(
                gym=gym,
                created_at__lte=end_date,
                valid_until__gte=start_date
            ).count()
            data['active_tickets'].append(active_tickets_count)

            purchased_tickets = Ticket.objects.filter(
                gym=gym,
                created_at__year=year,
                created_at__month=month
            )
            data['purchased_tickets'].append(purchased_tickets.count())

            ticket_usage = TicketEntrance.objects.filter(
                ticket__gym_id=gym.id,
                entrance_at__year=year,
                entrance_at__month=month
            ).count()
            data['tickets_usage'].append(ticket_usage)

            new_clients_count = Ticket.objects.filter(
                gym=gym,
                created_at__year=year,
                created_at__month=month,
            ).values('user').distinct().count()
            data['new_clients'].append(new_clients_count)

            earnings = purchased_tickets.aggregate(total_earnings=Sum('price'))['total_earnings'] or 0
            data['earnings'].append(earnings)

            promotions_agree_count = PromotionsAgree.objects.filter(
                gym=gym,
                created_at__year=year,
                created_at__month=month
            ).count()
            data['promotions_agree'].append(promotions_agree_count)

            newsletter_agree_count = NewsletterAgree.objects.filter(
                gym=gym,
                created_at__year=year,
                created_at__month=month
            ).count()
            data['newsletter_agree'].append(newsletter_agree_count)

        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No gym selected'}, status=400)


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

    for client in clients:
        client.summary_entrances = TicketEntrance.objects.filter(ticket__user=client, ticket__gym_id=gym.id).count()
        client.bought_tickets = Ticket.objects.filter(user=client, gym_id=gym.id).count()

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_clients',
        'clients': clients,
        'status_filter': status_filter,
    }

    return render(request, 'crm/gyms/gym_clients.html', context)


@gym_employee_allowed
def client_details(request, gym_id, client_id):
    gym = Gym.objects.get(id=gym_id)

    try:
        client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
        return redirect('gym_clients', gym_id=gym_id)

    if not check_if_client_is_connected_with_gym(gym, client):
        return redirect('gym_clients', gym_id=gym_id)

    tickets = Ticket.objects.filter(user=client, gym=gym)
    entrances = TicketEntrance.objects.filter(ticket__in=tickets)
    total_entrances = entrances.count()
    earliest_entrance = entrances.aggregate(Min('entrance_at'))['entrance_at__min']

    context = {
        'gym': gym,
        'client': client,
        'tickets': tickets,
        'total_entrances': total_entrances,
        'has_promotion_agree': PromotionsAgree.objects.filter(gym=gym, user=client).exists(),
        'has_newsletter_agree': NewsletterAgree.objects.filter(gym=gym, user=client).exists(),
        'earliest_entrance': earliest_entrance,
    }

    return render(request, 'crm/gyms/gym_client_details.html', context)


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
def gym_assortment(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_assortment',
        'gym': gym,
        'assortment': gym.assortments.all()
    }

    if request.method == "POST":

        if request.POST.get('action') == 'add_assortment':
            assortment = Assortment.objects.create(
                gym=gym,
                name=request.POST.get('name'),
                brand=request.POST.get('brand'),
                quantity=int(request.POST.get('quantity'))
            )

            photo = request.FILES.get('image')
            if photo:
                try:
                    image = Image.open(photo)
                except IOError:
                    return JsonResponse({'error': 'Unable to open image'}, status=400)

                png_buffer = BytesIO()
                image.save(png_buffer, format='PNG')
                png_buffer.seek(0)

                assortment.image.save(f'assortment_{gym.id}_{uuid4()}.png', png_buffer)

            return redirect('gym_assortment', gym_id=gym_id)

        if request.POST.get('action') == 'remove_assortment':
            assortment = Assortment.objects.get(id=request.POST.get('assortment_id'))

            if assortment.gym == gym:
                assortment.delete()
                return JsonResponse({'Msg': 'removed'}, status=200)

            return JsonResponse({'Msg': 'You dont have access'}, status=403)

        if request.POST.get('action') == 'edit_assortment':
            assortment = Assortment.objects.get(id=request.POST.get('assortment_id'))

            if assortment.gym == gym:
                assortment.name = request.POST.get('name')
                assortment.brand = request.POST.get('brand')
                assortment.quantity = request.POST.get('quantity')

                assortment.save()

                return redirect('gym_assortment', gym_id=gym_id)

            return JsonResponse({'Msg': 'You dont have access'}, status=403)

    return render(request, 'crm/gyms/gym_assortment.html', context)


@gym_employee_allowed
def gym_service(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_services',
        'gym': gym,
        'services': gym.services.all()
    }

    if request.method == "POST":
        if request.POST.get('action') == 'add_service':
            service = Services.objects.create(
                gym=gym,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
            )

            photo = request.FILES.get('image')
            if photo:
                try:
                    image = Image.open(photo)
                except IOError:
                    return JsonResponse({'error': 'Unable to open image'}, status=400)

                png_buffer = BytesIO()
                image.save(png_buffer, format='PNG')
                png_buffer.seek(0)

                service.image.save(f'service_{gym.id}_{uuid4()}.png', png_buffer)

            return redirect('gym_service', gym_id=gym_id)

    if request.POST.get('action') == 'remove_service':
        service = Services.objects.get(id=request.POST.get('service_id'))

        if service.gym == gym:
            service.delete()
            return JsonResponse({'Msg': 'removed'}, status=200)

        return JsonResponse({'Msg': 'You dont have access'}, status=403)

    if request.POST.get('action') == 'edit_service':
        service = Services.objects.get(id=request.POST.get('service_id'))

        if service.gym == gym:
            service.name = request.POST.get('name')
            service.description = request.POST.get('description')

            service.save()

            return redirect('gym_service', gym_id=gym_id)

        return JsonResponse({'Msg': 'You dont have access'}, status=403)

    return render(request, 'crm/gyms/gym_services.html', context)


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
        'gyms': Gym.objects.all(),
        'user_favorites': request.user.clientprofile.favorites_gyms.all()
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
