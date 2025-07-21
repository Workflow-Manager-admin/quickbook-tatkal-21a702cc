from rest_framework import serializers
from decimal import Decimal
from .models import UserProfile, Booking, PaymentTransaction

# PUBLIC_INTERFACE
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    wallet_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'age', 'address', 'preferred_berth',
            'wallet_balance', 'auto_fill_enabled',
        ]


# PUBLIC_INTERFACE
class BookingSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    user_profile_id = serializers.PrimaryKeyRelatedField(
        source='user_profile', queryset=UserProfile.objects.all(), write_only=True
    )
    fare = serializers.DecimalField(max_digits=8, decimal_places=2)
    preferred_berth = serializers.CharField()
    paid = serializers.BooleanField(read_only=True)
    paid_via_wallet = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user_profile', 'user_profile_id', 'source', 'destination', 'journey_date',
            'passenger_name', 'passenger_age', 'passenger_sex', 'preferred_berth', 'fare',
            'paid', 'paid_via_wallet', 'payment_time',
            'booking_status', 'pnr', 'booking_time', 'feedback'
        ]

    def validate(self, data):
        # PUBLIC_INTERFACE
        # Validate that ages are positive and fare is not negative
        if data['passenger_age'] <= 0:
            raise serializers.ValidationError("Passenger age must be positive number.")
        if 'fare' in data and data['fare'] < 0:
            raise serializers.ValidationError("Fare cannot be negative.")
        return data

# PUBLIC_INTERFACE
class DepositWalletSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= Decimal("0.0"):
            raise serializers.ValidationError("Deposit amount must be positive.")
        return value

# PUBLIC_INTERFACE
class BookingCreateSerializer(serializers.ModelSerializer):
    user_profile_id = serializers.PrimaryKeyRelatedField(
        source='user_profile', queryset=UserProfile.objects.all(), write_only=True
    )
    class Meta:
        model = Booking
        fields = [
            'user_profile_id', 'source', 'destination', 'journey_date',
            'passenger_name', 'passenger_age', 'passenger_sex', 'preferred_berth', 'fare'
        ]

    def validate(self, data):
        if data.get('passenger_age', 0) <= 0:
            raise serializers.ValidationError("Passenger age must be positive.")
        if data.get('fare', Decimal("0.0")) < 0:
            raise serializers.ValidationError("Fare cannot be negative.")
        return data

# PUBLIC_INTERFACE
class PaymentTransactionSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        source='booking', queryset=Booking.objects.all(), write_only=True
    )
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'booking', 'booking_id', 'order_id', 'payment_id', 'status',
            'amount', 'created_at', 'payment_response'
        ]
