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


class PromotionsAgree(Agreement):
    def __str__(self):
        return f'Promotion agree for {self.user.username} in gym {self.gym.name}'

class NewsletterAgree(Agreement):
    def __str__(self):
        return f'Newsletter agree for {self.user.username} in gym {self.gym.name}'

