import uuid

from django.core.validators import (
    FileExtensionValidator,
    MinLengthValidator,
    MinValueValidator,
    ValidationError,
)
from django.db import models
from django.utils import timezone

from .validators import alphanumeric_code_validator


def _today():
    """Current date in the active timezone (callable default for DateField)."""
    return timezone.now().date()


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Product ID"
    )
    sku = models.CharField(
        max_length=70,
        unique=True,
        validators=[alphanumeric_code_validator],
    )
    name = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(3, message="Name must be at least 3 characters long")
        ],
    )
    description = models.TextField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Unit price must be zero or greater")],
    )
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(
        upload_to="images/products/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "png", "gif"],
                message="Only JPG, PNG and GIF images are allowed",
            )
        ],
    )
    manufactured_date = models.DateField(default=_today)
    expiry_date = models.DateField(default=_today)

    class Meta:
        db_table = "products"
        ordering = ["-manufactured_date", "name"]
        indexes = [
            models.Index(fields=["name", "category"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "photo"], name="product_name_photo_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="product_unit_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.category} - {self.unit_price}"

    def clean(self):
        if self.manufactured_date > self.expiry_date:
            raise ValidationError("Manufactured date must be before expiry date")
