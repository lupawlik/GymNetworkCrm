from PIL import Image
from io import BytesIO
from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import render, redirect
from users.utils import panel_admin_allowed, gym_employee_allowed
from crm.models import BaseCompany, BaseCompanyAddress, Gym, GymAddress


def dashboard(request):
    context = {
        'segment': 'dashboard',
    }

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

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_clients'
    }

    return render(request, 'crm/network_clients.html', context)


@gym_employee_allowed
def gym_details(request, gym_id):
    gym = Gym.objects.get(id=gym_id)

    context = {
        'parent': 'your_gyms',
        'gym_id': gym.id,
        'segment': 'gym_details',
        'gym': gym
    }

    if request.method == "POST":
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

        return redirect('gym_details', gym_id=gym_id)

    return render(request, 'crm/gyms/gym_details.html', context)
