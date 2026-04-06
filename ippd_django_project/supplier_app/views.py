from rest_framework import viewsets

from .models import Supplier
from .serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().prefetch_related("products")
    serializer_class = SupplierSerializer
