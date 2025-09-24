from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('shoes', 'Shoes'),
        ('ball', 'Ball'),
        ('accessories', 'Accessories'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    thumbnail = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 

    def __str__(self):
        return f"{self.name} - Rp{self.price}"

    @property
    def is_out_of_stock(self):
        return self.stock <= 0

    def reduce_stock(self, amount=1):
        if self.stock >= amount:
            self.stock -= amount
            self.save()


