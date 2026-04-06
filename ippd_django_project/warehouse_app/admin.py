from django.contrib import admin

from .models import Inventory, Warehouse

admin.site.register(Warehouse)
admin.site.register(Inventory)
