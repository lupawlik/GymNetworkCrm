from django.utils.deprecation import MiddlewareMixin
from interactions.models import PushNotification
from users.utils import user_is_client


class PushNotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and user_is_client(request.user):
            request.unread_push = PushNotification.objects.filter(user=request.user, is_opened=False)
        else:
            request.unread_push = []
