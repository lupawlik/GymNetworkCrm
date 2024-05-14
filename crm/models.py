from django.db import models


class BaseAddressModel(models.Model):
    address_l1 = models.CharField(max_length=250)
    address_l2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250)
    zip_code = models.CharField(max_length=15)
    country = models.CharField(max_length=50, null=True, blank=False)
    phone_nr = models.CharField(max_length=20, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)


class BaseCompanyAddress(BaseAddressModel):
    pass

class BaseCompany(models.Model):
    vat_id = models.CharField(max_length=40, null=True, blank=False)
    company_name = models.CharField(max_length=100)
    address = models.ForeignKey(BaseCompanyAddress, on_delete=models.CASCADE)
