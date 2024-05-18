from django.contrib import admin

# Register your models here.

from .models import Plan, SubscriptionPayment, Coupon, SubscriptionTrack

admin.site.register(Plan)
admin.site.register(SubscriptionPayment)
admin.site.register(SubscriptionTrack)
admin.site.register(Coupon)