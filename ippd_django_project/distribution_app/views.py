from rest_framework import viewsets

from .models import DistributionCenter, Shipment, ShipmentItem
from .serializers import (
    DistributionCenterSerializer,
    ShipmentItemSerializer,
    ShipmentSerializer,
)


class DistributionCenterViewSet(viewsets.ModelViewSet):
    queryset = DistributionCenter.objects.all()
    serializer_class = DistributionCenterSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = (
        Shipment.objects.select_related("warehouse", "distribution_center")
        .prefetch_related("items__product")
        .all()
    )
    serializer_class = ShipmentSerializer


class ShipmentItemViewSet(viewsets.ModelViewSet):
    queryset = ShipmentItem.objects.select_related(
        "shipment__warehouse", "product"
    ).all()
    serializer_class = ShipmentItemSerializer
