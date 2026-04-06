from rest_framework import serializers

from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "purchase_order",
            "product",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "order_date",
            "expected_delivery_date",
            "status",
            "total_amount",
            "items",
        ]
