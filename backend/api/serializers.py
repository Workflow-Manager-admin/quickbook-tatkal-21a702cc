from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Booking, Payment

# PUBLIC_INTERFACE
class ProfileSerializer(serializers.ModelSerializer):
    """Serialize Profile objects."""
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serialize User (for basic info/output only)."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# PUBLIC_INTERFACE
class BookingSerializer(serializers.ModelSerializer):
    """Serialize Booking objects."""
    profile = ProfileSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'user', 'profile', 'payment_id', 'error_message')

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serialize for booking creation only, with basic validation and auto-user assignment."""
    class Meta:
        model = Booking
        exclude = ['status', 'payment_id', 'created_at', 'updated_at', 'error_message']

# PUBLIC_INTERFACE
class PaymentSerializer(serializers.ModelSerializer):
    """Serialize Payment objects."""
    booking = BookingSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'booking')

# PUBLIC_INTERFACE
class UserValidationSerializer(serializers.Serializer):
    """Validate user login or info."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
