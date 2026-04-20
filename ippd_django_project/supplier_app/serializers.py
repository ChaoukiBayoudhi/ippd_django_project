from rest_framework import serializers

from .models import Supplier, SupplierProduct


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "address",
            "is_active",
            "rating",
            "products",
        ]


class SupplierBriefSerializer(serializers.ModelSerializer):
    """Supplier fields without nested products (safe on product ↔ supplier endpoints)."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "is_active",
            "rating",
        ]


class SupplierProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "supplier",
            "product",
        ]
