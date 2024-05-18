
from users.models import User
from subscriptions.models import SubscriptionPayment, PlanType
from subscriptions.helper import get_end_date
from django.db.models import Q, Case, When, F
from django.utils import timezone
from math import ceil

"""Needed To be tested when user has subscription"""


def give_reward(user: User) -> None:
    print(user)
    subscriptions = SubscriptionPayment.objects.filter(
        user=user)
    
    subscription_ct = 0
    active_subscription: list[SubscriptionPayment] = []
    for subscription in subscriptions:
        end_date = get_end_date(subscription.start_date, subscription.duration, subscription.extra_days)
        if end_date>=timezone.now().date():
            subscription_ct+=1
            active_subscription.append(subscription)

    print(active_subscription)
    print(subscription_ct)

    if subscription_ct == 0:
        user.referral_ct += 1
        user.number_of_discounts += 1
        user.save()
    else:
        for subscription in active_subscription:
            subscription.extra_days += 4//subscription_ct if subscription.duration == PlanType.MONTHLY.value else 38//subscription_ct

def should_reward_refferal(user: User) -> bool:
    return user.refered_by and user.given_reward_to_referer == False


def check_and_reward_referer(user: User):
    if should_reward_refferal(user):
        give_reward(user.refered_by)
        user.given_reward_to_referer = True
        user.save()
