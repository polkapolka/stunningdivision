from django.contrib import admin
from .models import Address, Provider, TestingSite

# Register your models here.
admin.site.register(Address)
admin.site.register(Provider)
admin.site.register(TestingSite)
