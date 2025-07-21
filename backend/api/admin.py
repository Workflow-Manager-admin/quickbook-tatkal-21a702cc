from django.contrib import admin
from .models import UserProfile, TatkalBooking, PaymentTransaction

admin.site.register(UserProfile)
admin.site.register(TatkalBooking)
admin.site.register(PaymentTransaction)
