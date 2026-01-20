from django.db import models

# Create your models here.


class SellerRegistration(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    mob = models.CharField(max_length=10)
    password = models.CharField(max_length=8)
    add = models.TextField()
    accept = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Seller Registrations"
