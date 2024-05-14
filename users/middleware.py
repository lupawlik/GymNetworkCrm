from django.utils import timezone
from users.utils import user_is_panel_admin
from django.shortcuts import reverse, redirect


class LastUserRequest:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user
        if user.is_authenticated:
            user.last_activity = timezone.now()
            user.save()

        return response


class AdminPanelHasBaseCompany:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and user_is_panel_admin(request.user):
            if not request.user.adminpanelprofile.base_company and request.path != reverse('complete_info_about_base_company'):
                return redirect('complete_info_about_base_company')

        return response
