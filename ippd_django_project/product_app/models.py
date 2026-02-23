from django.db import models
from django.db.models import constraints, indexes
from django.db.models.fields import uuid

class Product(models.Model):
    id=models.UUIDField(primary_key=True,
    default=uuid.uuid4,
    editable=False)
    sku=models.CharField(max_length=70,unique=True)
    name=models.CharField(max_length=50)
    description=models.TextField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)
    photo=models.ImageField(upload_to='images/products/',blank=True,null=True)
    manufactured_date=models.DateField(auto_now_add=True)
    expiry_date=models.DateField(auto_now=True)

    class Meta:
        #custom table name
        db_table='products'
        #introducing ordering by manufactured date in descending order
        #and then by name in ascending order
        ordering=['-manufactured_date','name']

        indexes=[models.Index(fields=['name','category']),]
        constraints=[models.UniqueConstraint(fields=['name','photo'],name="product_name_photo_unique")]

    

    