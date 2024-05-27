from django.contrib import admin
from interactions.models import *

# Register your models here.
admin.site.register(Rating)
admin.site.register(RatingResponse)

admin.site.register(TicketTempCode)
