
from users.models import User
from subscriptions.models import SubscriptionPayment, PlanType
from django.db.models import Q, Case, When, F
from django.utils import timezone
from math import ceil

"""Needed To be tested when user has subscription"""
def give_reward(user: User) -> None:
    print(user)
    has_active_sub_query = Q(user=user) & Q(
        end_date__gte=timezone.now().date())
    subscriptions = SubscriptionPayment.objects.filter(
        has_active_sub_query)
    subscription_ct = subscriptions.count()
    print(has_active_sub_query)
    print(subscriptions)
    print(subscription_ct)
    if subscription_ct == 0:
        user.referral_ct += 1
        user.number_of_discounts += 1
        user.save()
    else:
        subscriptions.update(
            end_date=Case(
                When(type=PlanType.MONTHLY, then=F("end_date") +
                        timezone.timedelta(days=ceil(3, subscription_ct))),
                When(type=PlanType.ANNUAL, then=F("end_date") +
                        timezone.timedelta(days=ceil(37, subscription_ct))),
            )
        )
    


def should_reward_refferal(user: User) -> bool:
    return user.refered_by and user.given_reward_to_referer == False


def check_and_reward_referer(user:User):
    if should_reward_refferal(user):
        give_reward(user.refered_by)
        user.given_reward_to_referer = True
        user.save()

