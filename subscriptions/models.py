from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
# from ..apps_iq.models import App
from apps_iq.models import App

from users.models import User
from enum import Enum


class PlanType(Enum):
    MONTHLY = 'Monthly'
    ANNUAL = 'Annual'


class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    recommended = models.BooleanField(default=False)

    # store all the app for which this plan is applicable
    apps = models.ManyToManyField(App)

    def __str__(self):
        return self.name

    # @classmethod
    # def get_plan(cls, plan_id):
    #     try:
    #         plan = cls.objects.get(id=plan_id)
    #     except cls.DoesNotExist:
    #         plan = None
    #     return plan

    # def subscribe(self, user):
    #     @transaction.atomic
    #     def _ ():
    #         for app in self.apps.all():
    #             Subscription.objects.create(
    #                 user=user,
    #                 app=app,
    #                 end_date=timezone.now().date() +
    #                 timezone.timedelta(
    #                     days=30 if self.type == 'Monthly' else 365)
    #             )

    #         SubscriptionPayment.objects.create(
    #             user=user,
    #             plan=self,
    #             amount=self.price
    #         )
    #     with transaction.atomic():
    #         _()


# class Subscription(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     app = models.ForeignKey(App, on_delete=models.CASCADE)
#     start_date = models.DateField(default=timezone.now)
#     end_date = models.DateField()
#     # active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.app.app_name} Subscription"

#     @classmethod
#     def check_is_subscribed(cls, user, app):
#         subscription = cls.objects.filter(user=user, app=app).first()
#         if subscription and subscription.end_date >= timezone.now().date():
#             return True
#         return False

    # @classmethod
    # def get_subscription(cls, user, app):
    #     try:
    #         subscription = cls.objects.get(user=user, app=app)
    #     except cls.DoesNotExist:
    #         subscription = None
    #     return subscription

class SubscriptionTrackStatus(Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class SubscriptionTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=10, choices=[(
        tag.value, tag.value) for tag in PlanType], default=PlanType.MONTHLY.value)
    initiation_time = models.DateTimeField(default=timezone.now)
    payment_conformation_time = models.DateTimeField(default=None, null=True)
    payment_failed_time = models.DateTimeField(default=None, null=True)

    payment_status = models.CharField(max_length=20, choices=[(
        status.value, status.value) for status in SubscriptionTrackStatus], default=SubscriptionTrackStatus.INITIATED.value)

    def handle_success(self):
        self.payment_conformation_time = timezone.now()
        self.payment_status = SubscriptionTrackStatus.SUCCESS.value
        self.save()
        print("handle success: ", self)

    def handle_failure(self):
        self.payment_failed_time = timezone.now()
        self.payment_status = SubscriptionTrackStatus.FAILURE.value
        self.save()


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    duration = models.CharField(max_length=10, choices=[(
        tag.value, tag.value) for tag in PlanType], default=PlanType.MONTHLY.value)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateField(default=timezone.now)

    start_date = models.DateField(default=timezone.now)

    extra_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Payment for {self.plan.name}"

    @classmethod
    def on_successful_payment(cls, subscription_track: SubscriptionTrack) -> bool:
        subscription_payment = cls(
            user=subscription_track.user,
            plan=subscription_track.plan,
            duration=subscription_track.duration,
            amount=subscription_track.amount,
        )

        subscription_payment.save()
        print("subscription_payment: ", subscription_payment)
        return subscription_payment


class DiscountType(Enum):
    PERCENTAGE = 'percentage'
    FLAT = 'Flat'


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_in_decimal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    flat_discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=10, choices=[(
        tag.value, tag.value) for tag in DiscountType], default='percentage')

    def __str__(self):
        return self.code + " With discount of " + str(self.discount_in_decimal)
