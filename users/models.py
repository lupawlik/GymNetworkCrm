from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from crm.models import BaseCompany, Gym


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        ADMIN_PANEL = "ADMIN_PANEL", 'Admin Panel'
        CLIENT = "CLIENT", 'Client'
        EMPLOYEE = "EMPLOYEE", 'Employee'

    last_activity = models.DateTimeField(null=True)
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role

        return super().save(*args, **kwargs)


class AdminPanelManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.ADMIN_PANEL)


class AdminPanel(User):
    base_role = User.Role.ADMIN_PANEL
    admin_crm = AdminPanelManager()

    class Meta:
        proxy = True


class AdminPanelProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    base_company = models.ForeignKey(BaseCompany, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=AdminPanel)
def create_adminpanel_profile(sender, instance, created, **kwargs):
    if created and instance.role == "ADMIN_PANEL":
        AdminPanelProfile.objects.create(user=instance)


class ClientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.CLIENT)


class Client(User):
    base_role = User.Role.CLIENT
    admin_crm = ClientManager()

    class Meta:
        proxy = True


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=Client)
def create_client_profile(sender, instance, created, **kwargs):
    if created and instance.role == "CLIENT":
        ClientProfile.objects.create(user=instance)


class EmployeeManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.CLIENT)


class Employee(User):
    base_role = User.Role.EMPLOYEE
    admin_crm = EmployeeManager()

    class Meta:
        proxy = True


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    base_company = models.ForeignKey(BaseCompany, on_delete=models.SET_NULL, null=True)
    salary = models.FloatField(default=0)
    gyms = models.ManyToManyField(Gym, related_name='allowed_employees', null=True)


@receiver(post_save, sender=Employee)
def create_employee_profile(sender, instance, created, **kwargs):
    if created and instance.role == "EMPLOYEE":
        EmployeeProfile.objects.create(user=instance)


class UserFactory:
    @staticmethod
    def create_user(user_type, **kwargs):
        if user_type == User.Role.ADMIN_PANEL:
            return AdminPanel.objects.create(**kwargs)
        elif user_type == User.Role.CLIENT:
            return Client.objects.create(**kwargs)
        elif user_type == User.Role.EMPLOYEE:
            return Employee.objects.create(**kwargs)
