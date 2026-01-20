from django.db import models
from django.utils import timezone

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.email
    

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images')

    def __str__(self):
        return self.name 
    

class Registration(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    mob = models.CharField(max_length=10)
    password = models.CharField(max_length=8)
    add = models.TextField()

    def __str__(self):
        return self.email


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='pro_img')
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    
    def __str__(self):
        return self.name 


class Cart(models.Model):
    pro = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Registration,on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    order_id = models.PositiveIntegerField(default=0)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"User: {self.user.name} - Product: {self.pro.name} - Quantity: {self.qty}"


class Order(models.Model):
    prods = models.ManyToManyField(Cart)
    user = models.ForeignKey(Registration,on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.PositiveIntegerField()
    add = models.TextField()
    mob = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=6)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user) 



class Wishlist(models.Model):
    pro = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Registration,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) 


