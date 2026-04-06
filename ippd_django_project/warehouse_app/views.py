from rest_framework import viewsets

from .models import Inventory, Warehouse
from .serializers import InventorySerializer, WarehouseSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related("warehouse", "product").all()
    serializer_class = InventorySerializer
