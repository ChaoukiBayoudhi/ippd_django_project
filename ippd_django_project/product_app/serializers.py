from rest_framework import serializers

from .models import Product


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
