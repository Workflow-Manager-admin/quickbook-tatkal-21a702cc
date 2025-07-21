from django.urls import path

from .views import (
    health,
    user_profile_list_create,
    user_profile_detail,
    tatkal_booking_create,
    tatkal_booking_status,
    tatkal_booking_cancel,
    auto_fill_suggestions,
    payment_initiate,
    payment_callback,
    payment_status,
    # Custom core endpoints
    register_user,
    deposit_wallet,
    create_booking,
    get_profile,
    get_bookings
)

urlpatterns = [
    # Core endpoints
    path('register_user/', register_user, name='register_user'),
    path('deposit_wallet/', deposit_wallet, name='deposit_wallet'),
    path('create_booking/', create_booking, name='create_booking'),
    path('get_profile/<int:user_id>/', get_profile, name='get_profile'),
    path('get_bookings/<int:user_id>/', get_bookings, name='get_bookings'),

    # Existing endpoints
    path('health/', health, name='Health'),
    path('user_profiles/', user_profile_list_create, name='user_profile_list_create'),
    path('user_profiles/<int:user_id>/', user_profile_detail, name='user_profile_detail'),
    path('auto_fill/<int:user_profile_id>/', auto_fill_suggestions, name='auto_fill_suggestions'),
    path('bookings/', tatkal_booking_create, name='tatkal_booking_create'),
    path('bookings/<int:booking_id>/', tatkal_booking_status, name='tatkal_booking_status'),
    path('bookings/<int:booking_id>/cancel/', tatkal_booking_cancel, name='tatkal_booking_cancel'),
    path('payment/initiate/', payment_initiate, name='payment_initiate'),
    path('payment/callback/', payment_callback, name='payment_callback'),
    path('payment/<int:payment_transaction_id>/status/', payment_status, name='payment_status')
]
