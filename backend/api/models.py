from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# PUBLIC_INTERFACE
class UserProfile(models.Model):
    """
    Stores user profile data including full name, age, address, preferred berth, and wallet.
    Enables lightning-fast booking with personalized details and wallet for quick-pay.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=256)
    preferred_berth = models.CharField(max_length=16, choices=(
        ("lower", "Lower"),
        ("middle", "Middle"),
        ("upper", "Upper"),
        ("side_lower", "Side Lower"),
        ("side_upper", "Side Upper"),
        ("any", "Any"),
    ), default="any")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    auto_fill_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    # PUBLIC_INTERFACE
    def deposit_wallet(self, amount):
        """Add funds to wallet balance."""
        self.wallet_balance += Decimal(amount)
        self.save()

    # PUBLIC_INTERFACE
    def deduct_wallet(self, amount) -> bool:
        """Deduct funds from wallet if sufficient balance exists; returns True if successful, False otherwise."""
        amt = Decimal(amount)
        if self.wallet_balance >= amt:
            self.wallet_balance -= amt
            self.save()
            return True
        return False

    # PUBLIC_INTERFACE
    def can_afford(self, amount) -> bool:
        """Checks if wallet has at least `amount`."""
        return self.wallet_balance >= Decimal(amount)

# PUBLIC_INTERFACE
class Booking(models.Model):
    """
    Represents a single booking: source, destination, passenger details, berth, fare, paid-status, and wallet logic.

    Handles payment/quick-pay process with wallet deduction if selected.
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bookings')
    source = models.CharField(max_length=60)
    destination = models.CharField(max_length=60)
    journey_date = models.DateField()

    passenger_name = models.CharField(max_length=100)
    passenger_age = models.PositiveIntegerField()
    passenger_sex = models.CharField(max_length=10)

    preferred_berth = models.CharField(
        max_length=16,
        choices=(
            ("lower", "Lower"),
            ("middle", "Middle"),
            ("upper", "Upper"),
            ("side_lower", "Side Lower"),
            ("side_upper", "Side Upper"),
            ("any", "Any"),
        ),
        default="any"
    )
    fare = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    paid = models.BooleanField(default=False)
    paid_via_wallet = models.BooleanField(default=False)
    payment_time = models.DateTimeField(blank=True, null=True)
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
        return f"Booking #{self.pk}: {self.source}->{self.destination}, {self.passenger_name}"

    # PUBLIC_INTERFACE
    def try_pay_via_wallet(self) -> bool:
        """
        Attempt to pay fare from user wallet. Deducts fare, marks as paid if successful.
        Returns True if payment successful, else False.
        """
        if not self.paid and self.user_profile and self.fare and self.user_profile.can_afford(self.fare):
            if self.user_profile.deduct_wallet(self.fare):
                self.paid = True
                self.paid_via_wallet = True
                self.booking_status = "booked"
                self.save()
                return True
        return False

# (Legacy) Keep PaymentTransaction for backward compatibility; can be migrated out in next major revision
class PaymentTransaction(models.Model):
    """Represents payment transactions, including Razorpay integration tracking (legacy, may be deprecated)."""
    # Link to Booking for payment records; NOT required for quick-wallet-pay logic,
    # but kept for gateway/callback integration.
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', blank=True, null=True)
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
        return f"Payment for Booking {self.booking.pk if self.booking else 'N/A'}: {self.status}"
