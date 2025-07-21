from django.contrib import admin
from .models import UserProfile, Booking, PaymentTransaction

admin.site.register(UserProfile)
admin.site.register(Booking)
admin.site.register(PaymentTransaction)
