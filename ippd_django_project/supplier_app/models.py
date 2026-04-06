import uuid

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from product_app.models import Product
from product_app.validators import alphanumeric_code_validator

phone_validator = RegexValidator(
    regex=r"^\+216\d{8}$",
    message="Tunisian phone number must start with +216 and be 8 digits long",
)


class Supplier(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Supplier ID"
    )
    name = models.CharField(max_length=50)
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
    )
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0, message="Rating must be positive or zero"),
            MaxValueValidator(5.0, message="Rating must be less than or equal to 5.0"),
        ],
    )
    products = models.ManyToManyField(
        Product,
        related_name="supplier_products",
        through="SupplierProduct",
    )

    class Meta:
        db_table = "suppliers"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["rating"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=0) & models.Q(rating__lte=5),
                name="supplier_rating_between_0_5",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.email}"


class SupplierProduct(models.Model):
    """Through table for Supplier–Product M:N (explicit db_table for existing schema)."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = "suppliers_products"
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "product"],
                name="suppliers_products_supplier_id_product_id_a79c6028_uniq",
            ),
        ]
