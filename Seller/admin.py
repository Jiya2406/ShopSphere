from django.contrib import admin
from .models import *

# Register your models here.
class AdminSellerRegistration(admin.ModelAdmin):
    list_display = ['name', 'email', 'password']

admin.site.register(SellerRegistration, AdminSellerRegistration)
