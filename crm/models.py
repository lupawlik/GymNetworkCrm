from django.db import models

class BaseAddressModel(models.Model):
    address_l1 = models.CharField(max_length=250)
    address_l2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250)
    zip_code = models.CharField(max_length=15)
    country = models.CharField(max_length=50, null=True, blank=False)
    phone_nr = models.CharField(max_length=20, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f'{self.address_l1}, {self.zip_code} {self.city}'


class BaseCompanyAddress(BaseAddressModel):
    pass


class BaseCompany(models.Model):
    vat_id = models.CharField(max_length=40, null=True, blank=False)
    company_name = models.CharField(max_length=100)
    address = models.ForeignKey(BaseCompanyAddress, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.company_name}, {self.vat_id}'


class GymAddress(BaseAddressModel):
    pass


class Gym(models.Model):
    name = models.CharField(max_length=60, null=True, blank=True)
    base_company = models.ForeignKey(BaseCompany, null=False, on_delete=models.CASCADE, related_name='gyms')
    address = models.ForeignKey(GymAddress, on_delete=models.CASCADE, null=True, blank=False)

    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='gym_images/', null=True, blank=True)
    opening_time_from = models.TimeField(null=True, blank=True)
    opening_time_to = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.base_company.company_name} - {self.name}'

    def formatted_opening_time_to(self):
        if self.opening_time_to:
            return self.opening_time_to.strftime('%H:%M')
        else:
            return ''

    def formatted_opening_time_from(self):
        if self.opening_time_from:
            return self.opening_time_from.strftime('%H:%M')
        else:
            return ''

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(rating.score for rating in ratings) / len(ratings), 1)

        return

    def get_lowest_pricing(self):
        if self.pricing.exists():
            return self.pricing.order_by('price').first().price
        return None

    def get_highest_pricing(self):
        if self.pricing.exists():
            return self.pricing.order_by('-price').first().price
        return None


class GymPricing(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='pricing')
    name = models.CharField(max_length=50)
    price = models.FloatField()


class Assortment(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='assortments')
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='assortments/', null=True, blank=True)


class Services(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', null=True, blank=True)

