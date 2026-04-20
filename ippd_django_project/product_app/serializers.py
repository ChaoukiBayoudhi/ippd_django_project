from rest_framework import serializers

from .models import Product


class ProductSuppliersWriteSerializer(serializers.Serializer):
    """Payload for linking suppliers to a product (M2M via SupplierProduct)."""

    supplier_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
        help_text="Supplier primary keys to link to this product.",
    )

    def validate_supplier_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate supplier ids are not allowed.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "unit_price",
            "category",
            "is_active",
            "photo",
            "manufactured_date",
            "expiry_date",
        ]
