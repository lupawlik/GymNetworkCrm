from django.contrib import admin
from crm.models import *

admin.site.register(BaseCompany)
admin.site.register(BaseCompanyAddress)

admin.site.register(Gym)
admin.site.register(GymAddress)
admin.site.register(GymPricing)

admin.site.register(Assortment)
