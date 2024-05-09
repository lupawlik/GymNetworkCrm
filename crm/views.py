from django.shortcuts import render

def dashboard(request):
    context = {
        'segment': 'dashboard',
    }

    return render(request, 'crm/dashboard.html', context)
