from django.contrib import admin
from users.models import *

admin.site.register(User)

admin.site.register(AdminPanel)
admin.site.register(AdminPanelProfile)

admin.site.register(Client)
admin.site.register(ClientProfile)

admin.site.register(Employee)
admin.site.register(EmployeeProfile)

admin.site.register(Ticket)
