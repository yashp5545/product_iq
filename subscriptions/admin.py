from django.contrib import admin

# Register your models here.

from .models import Plan, SubscriptionPayment, Coupon

admin.site.register(Plan)
admin.site.register(SubscriptionPayment)
admin.site.register(Coupon)