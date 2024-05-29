from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User
from subscriptions.models import SubscriptionPayment, Plan, PlanType
from subscriptions.helper import get_end_date
from apps_iq.models import App, Module



def is_subscribed_to_plan(plan_id: int, user_id: int) -> bool:
    user = User.objects.get(id = user_id)
    subscription_payments = SubscriptionPayment.objects.filter(user = user.id, plan = plan_id)
    for subscription in subscription_payments:
        end_date = subscription.end_date
        print(end_date)
        if end_date >= timezone.now().date():
            return True
    return False