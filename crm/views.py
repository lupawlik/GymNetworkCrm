from django.shortcuts import render, redirect
from users.utils import panel_admin_allowed
from crm.models import BaseCompany, BaseCompanyAddress

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
