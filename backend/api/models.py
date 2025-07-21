from django.db import models
from django.contrib.auth.models import User

# PUBLIC_INTERFACE
class UserProfile(models.Model):
    """Stores predefined user data for lightning-fast booking."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=20)
    preferred_payment_mode = models.CharField(max_length=32, choices=(("razorpay", "Razorpay"), ("cash", "Cash"), ("card", "Card")))
    auto_fill_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

# PUBLIC_INTERFACE
class TatkalBooking(models.Model):
    """Represents a Tatkal ticket booking attempt."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bookings')
    train_no = models.CharField(max_length=10)
    journey_date = models.DateField()
    from_station = models.CharField(max_length=60)
    to_station = models.CharField(max_length=60)
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.PositiveIntegerField()
    passenger_sex = models.CharField(max_length=10)
    booking_status = models.CharField(
        max_length=16,
        choices=(
            ("initiated", "Initiated"),
            ("payment_pending", "Payment Pending"),
            ("booked", "Booked"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ),
        default="initiated"
    )
    pnr = models.CharField(max_length=20, blank=True, null=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking #{self.pk} ({self.booking_status})"

# PUBLIC_INTERFACE
class PaymentTransaction(models.Model):
    """Represents payment transactions, including Razorpay integration tracking."""
    booking = models.OneToOneField(TatkalBooking, on_delete=models.CASCADE, related_name='payment')
    order_id = models.CharField(max_length=64, blank=True, null=True)
    payment_id = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(
        max_length=16, 
        choices=(
            ("created", "Created"),
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
        ),
        default="created"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.pk}: {self.status}"
