from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User
from subscriptions.models import SubscriptionPayment, Plan, PlanType
from subscriptions.helper import get_end_date
from apps_iq.models import App, Module


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

def is_subscribed_to_app(app_id: int, user_id: int) -> bool:
    app = App.objects.get(id = app_id)
    user = User.objects.get(id = user_id)
    subscription_payments = SubscriptionPayment.objects.filter(user = user.id)
    for subscription in subscription_payments:
        end_date = subscription.end_date
        print(end_date)
        if end_date >= timezone.now().date() and len(subscription.plan.apps.filter(id = app.id))>0:
            return True
    return False

def is_allowed(__class: Module, __id, app_id, user_id):
    _instance = __class.objects.get(id = __id)
    if not _instance.subscription_required:
        return True
    if is_subscribed_to_app(app_id, user_id):
        return True
    return False

    