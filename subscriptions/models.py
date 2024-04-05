from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
# from ..apps_iq.models import App
from apps_iq.models import App

from users.models import User
from enum import Enum


class PlanType(Enum):
    monthly = 'Monthly'
    annual = 'Annual'


class Plan(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[
                            (tag, tag.value) for tag in PlanType])
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_annual = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    recommended = models.BooleanField(default=False)

    # store all the app for which this plan is applicable
    apps = models.ManyToManyField(App)

    def __str__(self):
        return self.name

    @classmethod
    def get_plan(cls, plan_id):
        try:
            plan = cls.objects.get(id=plan_id)
        except cls.DoesNotExist:
            plan = None
        return plan

    @classmethod
    def subscribe(cls, user, plan):
        plan = cls.get_plan(plan)
        if not plan:
            return None

        if (plan.type == PlanType.monthly):
            end_date = timezone.now() + timezone.timedelta(days=30)
        else:
            end_date = timezone.now() + timezone.timedelta(days=365)
        
        for app in plan.apps.all():
            Subscription.objects.create(
                user=user,
                app=app,
                end_date=end_date
            )
        
        SubscriptionPayment.objects.create(
            user=user,
            plan=plan,
            amount=plan.price_annual if plan.type == PlanType.annual else plan.price_monthly
        )


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    # active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.app.app_name} Subscription"

    @classmethod
    def check_is_subscribed(cls, user, app):
        subscription = cls.objects.filter(user=user, app=app).first()
        if subscription and subscription.end_date >= timezone.now().date():
            return True
        return False

    @classmethod
    def get_subscription(cls, user, app):
        try:
            subscription = cls.objects.get(user=user, app=app)
        except cls.DoesNotExist:
            subscription = None
        return subscription


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Payment for {self.subscription.app.app_name}"
