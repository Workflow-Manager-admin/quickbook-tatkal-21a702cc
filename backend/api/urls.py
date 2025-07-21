from django.urls import path
from .views import (
    health,
    user_profiles,
    book_ticket,
    booking_status,
    payment,
    validate_user,
)

urlpatterns = [
    path('health/', health, name='Health'),
    path('profiles/', user_profiles, name='Profiles'),  # GET/POST for profile management
    path('book_ticket/', book_ticket, name='BookTicket'),  # POST: booking
    path('booking_status/', booking_status, name='BookingStatus'),  # GET: status
    path('payment/', payment, name='Payment'),  # POST: payment
    path('validate_user/', validate_user, name='ValidateUser'),  # POST: user validation
]
