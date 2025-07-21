from django.db import models
from django.contrib.auth.models import User

# PUBLIC_INTERFACE
class Profile(models.Model):
    """Predefined user details for profile auto-fill."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=128)
    age = models.PositiveSmallIntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    payment_mode = models.CharField(max_length=40, default='razorpay')  # For flexibility
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

class Booking(models.Model):
    """A Tatkal ticket booking record."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('failed', 'Failed')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    train_no = models.CharField(max_length=10)
    journey_date = models.DateField()
    source = models.CharField(max_length=64)
    destination = models.CharField(max_length=64)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)

class Payment(models.Model):
    """Payment info for Razorpay integration."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    razorpay_order_id = models.CharField(max_length=128)
    razorpay_payment_id = models.CharField(max_length=128, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=16, default='created')  # created, paid, failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
