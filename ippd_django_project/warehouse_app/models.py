import uuid

from django.core.validators import MinValueValidator, ValidationError
from django.db import models
from django.db.models import F

from product_app.models import Product
from product_app.validators import alphanumeric_code_validator


class Warehouse(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Warehouse ID",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=255)
    capacity_sqft = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message="Capacity must be greater than zero")
        ],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "warehouses"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity_sqft__gt=0),
                name="warehouse_capacity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Inventory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Inventory ID",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventory_records",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        related_name="inventory_records",
    )
    quantity_on_hand = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0, message="On-hand quantity cannot be negative")
        ],
    )
    reorder_point = models.IntegerField(
        validators=[MinValueValidator(0, message="Reorder point cannot be negative")],
    )
    max_stock_level = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory"
        ordering = ["warehouse_id", "product_id"]
        indexes = [
            models.Index(fields=["warehouse", "product", "quantity_on_hand"]),
            models.Index(fields=["product", "quantity_on_hand"]),
            models.Index(fields=["last_updated"]),
            models.Index(fields=["quantity_on_hand"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"],
                name="unique_inventory_per_warehouse_product",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_on_hand__gte=0),
                name="inventory_qty_on_hand_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(reorder_point__gte=0),
                name="inventory_reorder_point_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(max_stock_level__gt=0),
                name="inventory_max_stock_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(reorder_point__lt=F("max_stock_level")),
                name="inventory_reorder_below_max",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.code} / {self.product.sku}: {self.quantity_on_hand}"

    def clean(self):
        if self.reorder_point >= self.max_stock_level:
            raise ValidationError(
                {"reorder_point": "Must be less than max_stock_level."}
            )
        if self.quantity_on_hand > self.max_stock_level:
            raise ValidationError(
                {"quantity_on_hand": "Cannot exceed max_stock_level."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
