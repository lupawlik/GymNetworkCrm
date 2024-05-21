from django import template
from users.utils import user_is_panel_admin, user_is_employee, user_is_client

register = template.Library()

@register.filter(name='is_admin_panel')
def is_admin_panel(user):
    return user_is_panel_admin(user)

@register.filter(name='is_employee')
def is_employee(user):
    return user_is_employee(user)

@register.filter(name='is_client')
def is_client(user):
    return user_is_client(user)
