from rest_framework import serializers
from .models import UserProfile, TatkalBooking, PaymentTransaction

# PUBLIC_INTERFACE
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'age', 'phone', 'preferred_payment_mode', 'auto_fill_enabled']

# PUBLIC_INTERFACE
class TatkalBookingSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    user_profile_id = serializers.PrimaryKeyRelatedField(
        source='user_profile', queryset=UserProfile.objects.all(), write_only=True
    )
    class Meta:
        model = TatkalBooking
        fields = ['id', 'user_profile', 'user_profile_id', 'train_no', 'journey_date', 'from_station', 'to_station',
                  'passenger_name', 'passenger_age', 'passenger_sex',
                  'booking_status', 'pnr', 'booking_time', 'feedback']

    def validate(self, data):
        # Add robust validation here
        if data['passenger_age'] < 0:
            raise serializers.ValidationError("Passenger age must be positive.")
        return data

# PUBLIC_INTERFACE
class PaymentTransactionSerializer(serializers.ModelSerializer):
    booking = TatkalBookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        source='booking', queryset=TatkalBooking.objects.all(), write_only=True
    )
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'booking', 'booking_id', 'order_id', 'payment_id', 'status', 'amount', 'created_at', 'payment_response']
