from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User
from subscriptions.models import SubscriptionPayment, Plan, PlanType
from subscriptions.helper import get_end_date
from apps_iq.models import App


def isSubscribed(func):
    def wrapper(request, user, app_id,  *args, **kwargs):
        print("request, ", app_id)
        print("user", user)

        userObj = User.objects.get(id = user['id'])
        appObj = App.objects.get(id = app_id)
        print(appObj)

        subscription_payments = SubscriptionPayment.objects.filter(user = userObj.id)
        for subscription in subscription_payments:
            end_date = get_end_date(subscription.start_date, subscription.duration, subscription.extra_days)
            print(end_date)
            if end_date >= timezone.now().date() and len(subscription.plan.apps.filter(id = appObj.id))>0:
                return func(request, user, app_id,  *args, **kwargs)
        return Response({"error": f"You are not subscribed to {appObj.app_name}!"}, status=403)

    return wrapper
