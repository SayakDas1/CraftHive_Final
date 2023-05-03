from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):    
    is_customer = models.BooleanField('Is customer', default=False)
    is_seller = models.BooleanField('Is seller', default=False)

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    seller_name = models.CharField(max_length=50,default="")
    seller_email = models.EmailField(max_length = 254,default="")
    link = models.CharField(max_length=500, default="")
    stock = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField(default=date.today)
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")


    def __str__(self):
        return self.name

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField( default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")

class OrderUpdate(models.Model):
    update_id  = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return "Order ID: "+str(self.order_id)
    
class Review(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    comment = models.TextField(max_length=250,default='comment')
    rate = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)