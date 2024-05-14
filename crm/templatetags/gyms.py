from django import template

from users.utils import user_is_panel_admin
register = template.Library()

@register.simple_tag(takes_context=True)
def get_my_gyms(context):
    user = context['user']

    if user_is_panel_admin(user):
        return user.adminpanelprofile.base_company.gyms.all()

    return []
