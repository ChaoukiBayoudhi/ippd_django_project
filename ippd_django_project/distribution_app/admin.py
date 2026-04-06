from django.contrib import admin

from .models import DistributionCenter, Shipment, ShipmentItem

admin.site.register(DistributionCenter)
admin.site.register(Shipment)
admin.site.register(ShipmentItem)
