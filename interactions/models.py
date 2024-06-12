from django.db import models
from users.models import User
from crm.models import Gym
import random
from django.utils import timezone


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('user', 'gym')

    def __str__(self):
        return f"{self.user.username} - {self.gym.name}(id. {self.gym.id})"


class RatingResponse(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='self_responses', on_delete=models.CASCADE)


class TicketTempCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    ticket_id = models.IntegerField(null=True, blank=False)
    code = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.valid_until:
            self.valid_until = timezone.now() + timezone.timedelta(seconds=60)

        if not self.code:
            self.code = str(random.randint(1000000, 9999999))

        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.valid_until

    def __str__(self):
        return f'Code for {self.user.username} at {self.gym.name} - {self.code}'


class Agreement(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class PromotionsAgree(Agreement):
    def __str__(self):
        return f'Promotion agree for {self.user.username} in gym {self.gym.name}'


class NewsletterAgree(Agreement):
    def __str__(self):
        return f'Newsletter agree for {self.user.username} in gym {self.gym.name}'


class Campaign(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='camapaigns', null=True, blank=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50,
                            choices=(('push', 'Push Notification'), ('mail', 'Mail'), ('phone', 'Phone')))
    clients = models.ManyToManyField(User)
    status = models.CharField(max_length=50, default='ongoing')

    def __str__(self):
        return self.title

    @property
    def opened_by(self):
        return f"{self.push_notifications.filter(is_opened=True).count()} / {self.push_notifications.all().count()}"

    @property
    def opened_by_clients(self):
        return self.push_notifications.filter(is_opened=True)


class PushNotification(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='push_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.user.username}"


class EmailNotification(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.user.username}"
