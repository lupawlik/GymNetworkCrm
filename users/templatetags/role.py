from django import template
from users.utils import user_is_panel_admin

register = template.Library()

@register.filter(name='is_admin_panel')
def is_admin_panel(user):
    return user_is_panel_admin(user)
