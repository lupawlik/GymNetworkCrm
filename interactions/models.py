from django.db import models
from users.models import User
from crm.models import Gym


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
    parent = models.ForeignKey('self', null=True, blank=True, related_name='responses', on_delete=models.CASCADE)
