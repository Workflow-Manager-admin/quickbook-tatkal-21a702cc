from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Profile, Booking, Payment
from .serializers import (
    ProfileSerializer,
    BookingSerializer,
    PaymentSerializer,
    UserValidationSerializer,
)
import os

def get_env(var, default=None):
    """Utility for fetching .env vars."""
    return os.environ.get(var, default)

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def user_profiles(request):
    """
    Get or create/update user predefined profiles.

    - GET: List all profiles for current user.
    - POST: Create or update a user profile for autofill.
    """
    if request.method == 'GET':
        profiles = Profile.objects.filter(user=request.user)
        return Response(ProfileSerializer(profiles, many=True).data)
    else:
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            # For POST, use or create profile for this user (may use additional logic for 'update')
            profile = serializer.save(user=request.user)
            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def book_ticket(request):
    """
    Initiate a Tatkal ticket booking.

    Required fields: train_no, journey_date (yyyy-mm-dd), source, destination.
    Optional: profile_id for autofill.
    """
    data = request.data
    errors = {}

    # Robust validation
    for field in ['train_no', 'journey_date', 'source', 'destination']:
        if not data.get(field):
            errors[field] = "This field is required."
    if errors:
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    # Use profile for auto-fill
    profile = None
    if data.get('profile_id'):
        try:
            profile = Profile.objects.get(id=data['profile_id'], user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Save booking
    booking = Booking.objects.create(
        user=request.user,
        profile=profile,
        train_no=data['train_no'],
        journey_date=data['journey_date'],
        source=data['source'],
        destination=data['destination'],
        status='pending'
    )
    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def booking_status(request):
    """
    Fetch the status of all bookings for the current user.
    Query param: id (optional, for specific booking)
    """
    booking_id = request.query_params.get('id')
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            return Response(BookingSerializer(booking).data)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return Response(BookingSerializer(bookings, many=True).data)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def payment(request):
    """
    Initiate a payment for a booking via Razorpay.

    Required: booking_id
    Returns: Razorpay order (dummy/stub: replace with real integration)
    """
    from datetime import datetime
    data = request.data
    booking_id = data.get('booking_id')
    if not booking_id:
        return Response({'error': 'booking_id required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    if hasattr(booking, 'payment'):
        return Response({'error': 'Payment already initiated for this booking.'}, status=status.HTTP_409_CONFLICT)

    # Simplified order creation (Replace with Razorpay logic and order creation as needed)
    # Credentials from .env, don't hard-code
    key_id = get_env('RAZORPAY_KEY_ID')
    key_secret = get_env('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        return Response({'error': 'Payment gateway not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    dummy_razorpay_order_id = f'order_{booking.id}_{int(datetime.now().timestamp())}'

    pay = Payment.objects.create(
        booking=booking,
        razorpay_order_id=dummy_razorpay_order_id,
        status='created'
    )
    return Response(PaymentSerializer(pay).data, status=status.HTTP_201_CREATED)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_user(request):
    """
    Validate user credentials.

    Returns user info if valid, error otherwise.
    """
    serializer = UserValidationSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            return Response({"valid": True, "user_id": user.id, "username": user.username})
        else:
            return Response({"valid": False, "error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
