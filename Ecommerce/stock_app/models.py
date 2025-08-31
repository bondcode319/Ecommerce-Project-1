from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('home', 'Home & Garden'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    imageUrl = models.URLField(max_length=200, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']


# Remove custom User model since Django's built-in User is being used
# If you need additional user fields, create a Profile model instead:

class UserProfile(models.Model):
    """
    Extended user information - use this instead of creating a custom User model
    when you're already using Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=60, blank=True, null=False)
    department = models.CharField(max_length=100, blank=True, null=False)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Add other custom fields as needed

    def __str__(self):
        return f"{self.user.username}'s Profile"


class ProductChangeHistory(models.Model):
    """
    Model to track changes to the stock quantity of a product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='change_history')
    old_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='product_changes')
    reason = models.CharField(max_length=200, blank=True, null=True)  # Optional: reason for change

    def __str__(self):
        return f"Change for {self.product.name} by {self.user.username if self.user else 'Unknown'}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Product Change Histories"