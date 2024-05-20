from django import template

from users.utils import user_is_panel_admin, user_is_employee
register = template.Library()

@register.simple_tag(takes_context=True)
def get_my_gyms(context):
    user = context['user']

    if user_is_panel_admin(user):
        if not user.adminpanelprofile.base_company:
            return []
        return user.adminpanelprofile.base_company.gyms.all()

    if user_is_employee(user):
        if not user.employeeprofile.base_company:
            return []
        return user.employeeprofile.gyms.all()

    return []
