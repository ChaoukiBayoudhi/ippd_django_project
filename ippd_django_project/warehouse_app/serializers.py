from rest_framework import serializers

from .models import Inventory, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "id",
            "code",
            "name",
            "location",
            "capacity_sqft",
            "is_active",
        ]


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            "id",
            "warehouse",
            "product",
            "quantity_on_hand",
            "reorder_point",
            "max_stock_level",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]
