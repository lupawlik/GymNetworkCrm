from django.shortcuts import render

def dashboard(request):
    context = {
        'parent': 'dashboard',
    }

    return render(request, 'crm/dashboard.html', context)
