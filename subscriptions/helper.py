from users.models import User
from .models import Plan, SubscriptionPayment, SubscriptionTrack, PlanType, SubscriptionTrackStatus
from django.utils import timezone

def handle_checkout_session(session):
    subscription_track = SubscriptionTrack.objects.get(id= session.metadata['subscription_track_id'])
    if(subscription_track.payment_status == SubscriptionTrackStatus.SUCCESS):
        return
    print("session: ", session)
    
    SubscriptionPayment.on_successful_payment(subscription_track=subscription_track)
    subscription_track.handle_success()
    return True

def handle_checkout_session_failure(session):
    subscription_track = SubscriptionTrack.objects.get(id= session.metadata['subscription_track_id'])
    subscription_track.handle_failure()
    return True

def get_end_date(start_date, duration: PlanType):
    if(duration == PlanType.MONTHLY):
        return start_date+timezone.timedelta(days=30)
    elif duration == PlanType.ANNUAL:
        return start_date+timezone.timedelta(days=365)
