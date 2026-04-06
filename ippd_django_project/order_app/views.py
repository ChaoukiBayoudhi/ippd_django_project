from rest_framework import viewsets

from .models import PurchaseOrder, PurchaseOrderItem
from .serializers import PurchaseOrderItemSerializer, PurchaseOrderSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    #select_related is used to prefetch the related objects
    #this query returns the purchase orders with the supplier and the items with the product
    queryset = (
        PurchaseOrder.objects.select_related("supplier")
        .prefetch_related("items__product") #prefetch_related is used to prefetch the related objects
        .all()
    )
    serializer_class = PurchaseOrderSerializer


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.select_related(
        "purchase_order", "product"
    ).all()
    serializer_class = PurchaseOrderItemSerializer
