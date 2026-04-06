import uuid

from django.core.validators import MinValueValidator, ValidationError
from django.db import models
from django.db.models import F

from product_app.models import Product
from product_app.validators import alphanumeric_code_validator
from supplier_app.models import Supplier


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        CONFIRMED = "CONFIRMED", "Confirmed"
        IN_TRANSIT = "IN_TRANSIT", "In transit"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Purchase order ID",
    )
    order_number = models.CharField(
        max_length=64,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.RESTRICT,
        related_name="purchase_orders",
    )
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "purchase_orders"
        ordering = ["-order_date", "order_number"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["order_date"]),
            models.Index(fields=["supplier", "status", "order_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expected_delivery_date__gt=F("order_date")),
                name="purchase_order_delivery_after_order_date",
            ),
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=0),
                name="purchase_order_total_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order_number} ({self.status})"

    def calculate_total(self):
        from decimal import Decimal

        from django.db.models import Sum

        total = self.items.aggregate(total=Sum("subtotal"))["total"]
        if total is None:
            return Decimal("0")
        return total

    def clean(self):
        if self.expected_delivery_date <= self.order_date:
            raise ValidationError(
                {"expected_delivery_date": "Must be after order_date."}
            )
        if self.pk:
            computed = self.calculate_total()
            if self.total_amount != computed:
                raise ValidationError(
                    {
                        "total_amount": "Must equal the sum of line item subtotals "
                        f"(expected {computed})."
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        related_name="purchase_order_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Unit price must be zero or greater")],
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "purchase_order_items"
        ordering = ["purchase_order_id", "id"]
        indexes = [
            models.Index(fields=["quantity"]),
            models.Index(fields=["purchase_order", "product"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["purchase_order", "product"],
                name="unique_product_per_purchase_order",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="po_item_qty_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="po_item_unit_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="po_item_subtotal_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.purchase_order_id} × {self.product_id} ({self.quantity})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Must be positive."})
        if self.unit_price < 0:
            raise ValidationError({"unit_price": "Must be zero or greater."})

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        self.full_clean()
        super().save(*args, **kwargs)
