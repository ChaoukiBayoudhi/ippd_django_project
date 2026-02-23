from django.db import models

class Product(models.Model):
    id=models.UUIDField(primary_key=True, editable=False)
    sku=models.CharField(max_length=70,unique=True)
    name=models.CharField(max_length=50)
    description=models.TextField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)
    photo=models.ImageField(upload_to='images/products/',blank=True,null=True)
    manufactured_date=models.DateField(auto_now_add=True)
    expiry_date=models.DateField(auto_now=True)
    

    