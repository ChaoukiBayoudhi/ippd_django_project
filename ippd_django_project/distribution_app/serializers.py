from rest_framework import serializers

from .models import DistributionCenter, Shipment, ShipmentItem


class DistributionCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionCenter
        fields = [
            "id",
            "code",
            "name",
            "location",
            "service_region",
            "is_active",
        ]


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = ["id", "shipment", "product", "quantity"]


class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "shipment_number",
            "warehouse",
            "distribution_center",
            "ship_date",
            "expected_arrival_date",
            "status",
            "carrier",
            "items",
        ]
