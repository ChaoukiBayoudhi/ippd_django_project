import uuid

from django.core.validators import ValidationError
from django.db import models
from django.db.models import F

from product_app.models import Product
from product_app.validators import alphanumeric_code_validator
from warehouse_app.models import Inventory, Warehouse


class DistributionCenter(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Distribution center ID",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=255)
    service_region = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "distribution_centers"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_TRANSIT = "IN_TRANSIT", "In transit"
        DELIVERED = "DELIVERED", "Delivered"
        DELAYED = "DELAYED", "Delayed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Shipment ID",
    )
    shipment_number = models.CharField(
        max_length=64,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.RESTRICT,
        related_name="shipments",
    )
    distribution_center = models.ForeignKey(
        DistributionCenter,
        on_delete=models.RESTRICT,
        related_name="shipments",
    )
    ship_date = models.DateField()
    expected_arrival_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    carrier = models.CharField(max_length=120)

    class Meta:
        db_table = "shipments"
        ordering = ["-ship_date", "shipment_number"]
        indexes = [
            models.Index(fields=["shipment_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["ship_date"]),
            models.Index(fields=["warehouse", "status", "ship_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expected_arrival_date__gt=F("ship_date")),
                name="shipment_arrival_after_ship_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.shipment_number} ({self.status})"

    def clean(self):
        if self.expected_arrival_date <= self.ship_date:
            raise ValidationError(
                {"expected_arrival_date": "Must be after ship_date."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        related_name="shipment_items",
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "shipment_items"
        ordering = ["shipment_id", "id"]
        indexes = [
            models.Index(fields=["shipment", "product"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["shipment", "product"],
                name="unique_product_per_shipment",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="shipment_item_qty_positive"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.shipment_id} × {self.product_id} ({self.quantity})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Must be positive."})
        shipment = self.shipment
        if shipment is None:
            return
        wid = shipment.warehouse_id
        if not wid or not self.product_id:
            return
        inv = (
            Inventory.objects.filter(
                warehouse_id=wid,
                product_id=self.product_id,
            )
            .first()
        )
        available = inv.quantity_on_hand if inv else 0
        if self.quantity > available:
            raise ValidationError(
                {
                    "quantity": (
                        f"Exceeds available stock at source warehouse "
                        f"({available} on hand)."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
