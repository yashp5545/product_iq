from users.models import User
from .models import Plan, SubscriptionPayment, SubscriptionTrack, PlanType, SubscriptionTrackStatus, Coupon
from django.utils import timezone


def handle_checkout_session(session):
    subscription_track = SubscriptionTrack.objects.get(
        id=session.metadata['subscription_track_id'])
    if (subscription_track.payment_status == SubscriptionTrackStatus.SUCCESS):
        return
    print("session: ", session)
    subscription_track.handle_success()
    SubscriptionPayment.on_successful_payment(subscription_track=subscription_track)
    user = User.objects.get(id = subscription_track.user.id)
    user.reduce_number_of_discount(int(session.metadata['number_of_discount_to_reduce']))
    return True


def handle_checkout_session_failure(session):
    subscription_track = SubscriptionTrack.objects.get(
        id=session.metadata['subscription_track_id'])
    subscription_track.handle_failure()
    return True


def get_end_date(start_date, duration: PlanType, extra_days = 0):
    if (duration == PlanType.MONTHLY.value):
        print(start_date)
        return start_date + timezone.timedelta(days=30+extra_days)
    elif duration == PlanType.FOURMONTHS.value:
        return start_date + timezone.timedelta(days=120+extra_days)
    else:
        raise "In get_end_date function there is a error of duration"


def get_number_of_discount(user: User):
    number_of_discount = user.number_of_discounts
    if (number_of_discount > 10):
        number_of_discount = (10)
    return number_of_discount

def get_discounted_price(plan: Plan, duration: PlanType, number_of_discount: int, coupon_discount: float) -> float:
    FACTOR = 0.1
    plan_amount = plan.monthly_price if duration == PlanType.MONTHLY else plan.annual_price
    return max(
        float(plan_amount)
        - (float(plan_amount) * (number_of_discount * FACTOR))
        - (float(plan_amount) * coupon_discount),
        0
    )

def get_coupon_discount(coupon: str) -> int:
    coupon_discount = 0
    if coupon:
        coupon = Coupon.objects.filter(code=coupon).first()
        if not coupon:
            return -1
        coupon_discount = float(coupon.discount_in_decimal)
    return coupon_discount