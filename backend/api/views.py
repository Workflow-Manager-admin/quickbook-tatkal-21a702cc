from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.contrib.auth.models import User
from .models import UserProfile, TatkalBooking, PaymentTransaction
from .serializers import UserProfileSerializer, TatkalBookingSerializer, PaymentTransactionSerializer

import random
import string

# Dummy Razorpay setup (Replace with real integration, fetch keys from env)
RAZORPAY_MOCK_KEY = "rzp_test_mocked"
RAZORPAY_MOCK_SECRET = "secret_key_mocked"

@api_view(['GET'])
def health(request):
    """API Health Check."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def user_profile_list_create(request):
    """
    Get all user profiles or create a new user profile with predefined data.

    POST body: {username, password, full_name, age, phone, preferred_payment_mode, auto_fill_enabled}
    """
    if request.method == 'GET':
        profiles = UserProfile.objects.all()
        return Response(UserProfileSerializer(profiles, many=True).data)

    # Create user and profile
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"error": "Username and password required."}, status=drf_status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists."}, status=drf_status.HTTP_400_BAD_REQUEST)
    user = User(username=username)
    user.set_password(password)
    user.save()

    profile_data = {
        "user": user.id,
        "full_name": request.data.get("full_name"),
        "age": request.data.get("age"),
        "phone": request.data.get("phone"),
        "preferred_payment_mode": request.data.get("preferred_payment_mode", "razorpay"),
        "auto_fill_enabled": request.data.get("auto_fill_enabled", True)
    }
    serializer = UserProfileSerializer(data=profile_data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=drf_status.HTTP_201_CREATED)
    else:
        user.delete()
        return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def user_profile_detail(request, user_id):
    """
    Retrieve, update, or delete a user profile.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except Exception:
        return Response({"error": "User profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response({"deleted": True})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def tatkal_booking_create(request):
    """
    Initiate a fast Tatkal booking. Includes robust validation and status feedback.

    POST body: {
        user_profile_id, train_no, journey_date, from_station, to_station,
        passenger_name, passenger_age, passenger_sex
    }
    """
    serializer = TatkalBookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save(booking_status="payment_pending")
        return Response(TatkalBookingSerializer(booking).data, status=drf_status.HTTP_201_CREATED)
    return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def tatkal_booking_status(request, booking_id):
    """
    Track booking status (initiated/payment_pending/booked/failed/cancelled) and PNR.

    Params: booking_id
    """
    try:
        booking = TatkalBooking.objects.get(id=booking_id)
        return Response(TatkalBookingSerializer(booking).data)
    except TatkalBooking.DoesNotExist:
        return Response({"error": "Booking not found."}, status=drf_status.HTTP_404_NOT_FOUND)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def tatkal_booking_cancel(request, booking_id):
    """
    Cancel an existing booking by ID.
    """
    try:
        booking = TatkalBooking.objects.get(id=booking_id)
        if booking.booking_status not in ["booked", "initiated", "payment_pending"]:
            return Response({"error": "Cannot cancel this booking."}, status=drf_status.HTTP_400_BAD_REQUEST)
        booking.booking_status = "cancelled"
        booking.feedback = request.data.get("feedback", "")
        booking.save()
        return Response({"success": "Booking cancelled."}, status=drf_status.HTTP_200_OK)
    except TatkalBooking.DoesNotExist:
        return Response({"error": "Booking not found."}, status=drf_status.HTTP_404_NOT_FOUND)

# PUBLIC_INTERFACE
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def auto_fill_suggestions(request, user_profile_id):
    """
    Enables auto-filling forms using saved user profile data.
    GET returns the profile data for pre-filling booking UI.
    POST updates the auto-fill setting for the profile.
    """
    try:
        profile = UserProfile.objects.get(id=user_profile_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=drf_status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        data = UserProfileSerializer(profile).data
        return Response({k: data[k] for k in ['full_name', 'age', 'phone', 'preferred_payment_mode', 'auto_fill_enabled']})
    elif request.method == 'POST':
        profile.auto_fill_enabled = request.data.get('auto_fill_enabled', profile.auto_fill_enabled)
        profile.save()
        return Response({"auto_fill_enabled": profile.auto_fill_enabled})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_initiate(request):
    """
    Initiates a payment session for a Tatkal booking.
    POST body: { booking_id, amount }

    Simulates Razorpay payment initiation and returns order ID and payment link.
    """
    booking_id = request.data.get("booking_id")
    amount = request.data.get("amount")
    try:
        booking = TatkalBooking.objects.get(id=booking_id)
    except TatkalBooking.DoesNotExist:
        return Response({"error": "Booking not found."}, status=drf_status.HTTP_404_NOT_FOUND)

    # Simulate creation of a Razorpay order
    order_id = "order_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    payment_txn = PaymentTransaction.objects.create(
        booking=booking, order_id=order_id, status="pending", amount=amount
    )
    # This would be replaced by a real Razorpay payment_url
    payment_url = f"https://checkout.razorpay.com/v1/checkout.js?order_id={order_id}&key_id={RAZORPAY_MOCK_KEY}"

    return Response({
        "success": True,
        "order_id": order_id,
        "payment_url": payment_url,
        "payment_transaction_id": payment_txn.id
    })

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_callback(request):
    """
    Handles Razorpay payment callback (mocked for demo).
    POST body: { payment_transaction_id, payment_id, status }
    """
    payment_transaction_id = request.data.get("payment_transaction_id")
    payment_id = request.data.get("payment_id")
    status_str = request.data.get("status", "success")
    try:
        payment = PaymentTransaction.objects.get(id=payment_transaction_id)
    except PaymentTransaction.DoesNotExist:
        return Response({"error": "Payment transaction not found."}, status=drf_status.HTTP_404_NOT_FOUND)
    payment.payment_id = payment_id
    payment.status = "success" if status_str == "success" else "failed"
    # Mark booking accordingly
    booking = payment.booking
    if payment.status == "success":
        booking.booking_status = "booked"
        # Generate dummy PNR
        booking.pnr = ''.join(random.choices(string.digits, k=10))
    else:
        booking.booking_status = "failed"
    booking.save()
    payment.save()
    return Response({"booking_status": booking.booking_status, "pnr": booking.pnr})

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def payment_status(request, payment_transaction_id):
    """
    Returns status on payment transaction for a booking.
    """
    try:
        payment = PaymentTransaction.objects.get(id=payment_transaction_id)
        return Response(PaymentTransactionSerializer(payment).data)
    except PaymentTransaction.DoesNotExist:
        return Response({"error": "Payment transaction not found."}, status=drf_status.HTTP_404_NOT_FOUND)
