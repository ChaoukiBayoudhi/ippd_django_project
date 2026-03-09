from django.db import models
from django.db.models import constraints, indexes
from django.db.models.fields import timezone, uuid
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    RegexValidator,
    FileExtensionValidator,
    ValidationError,
)


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Product ID"
    )
    sku = models.CharField(max_length=70, unique=True)
    name = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(3, message="Name must be at least 3 characters long")
        ],
    )
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
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
    #when using auto_now_add=True, the date will be set to the current date and time when the object is created
    #if we want to enter the date manually, we can use auto_now=False
    manufactured_date = models.DateField(default=timezone.now().date())
    expiry_date = models.DateField(default=timezone.now().date())

    class Meta:
        # custom table name
        db_table = "products"
        # introducing ordering by manufactured date in descending order
        # and then by name in ascending order
        ordering = ["-manufactured_date", "name"]

        indexes = [
            models.Index(fields=["name", "category"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "photo"], name="product_name_photo_unique"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.category} - {self.unit_price}"

    # redefining the clean method to validate dates (manufactured date and expiry date)
    def clean(self):
        if self.manufactured_date > self.expiry_date:
            raise ValidationError("Manufactured date must be before expiry date")


# if the phone validation is needed in multiple models,
# it is better to define it as a separate validator function
phone_validator = RegexValidator(
    regex=r"^\+216\d{8}$",
    message="Tunisian phone number must start with +216 and be 8 digits long",
)


class Supplier(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Supplier ID"
    )
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
    )
    # the use of the prefix "r" is to treat the string as a raw string,
    # without interpreting escape characters like \d for digits
    # validators=[RegexValidator(regex=r'^\+216\d{8}$',
    # message="Tunisian phone number must start with +216 and be 8 digits long")
    # ])
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
    # validators value is used to validate the rating value
    # if the rating value is not in the range of 0.0 to 5.0, the value will not be saved
    # if the rating value is in the range of 0.0 to 5.0, the value will be saved
    # relationship between supplier and product is many to many
    # related_name value is used to get the products from the supplier when writing queries

    products = models.ManyToManyField(Product, related_name="supplier_products")

    class Meta:
        db_table = "suppliers"
        # ordering table rows by name in ascending order
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "code"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.email}"
