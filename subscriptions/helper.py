from users.models import User
from .models import Plan, SubscriptionPayment, SubscriptionTrack, PlanType
from django.utils import timezone
def handle_checkout_session(session):
    
    user = User.objects.get(id=session.metadata['user_id'])
    plan = Plan.objects.get(id=session.metadata['plan_id'])
    plan.subscribe(user)

    subscription_track_id = session.metadata['subscription_track_id']
    subscription_track = SubscriptionTrack.objects.get(id= subscription_track_id)
    subscription_track.handle_success()
    SubscriptionPayment.on_successful_payment(subscription_track=subscription_track)
    return True

def get_end_date(start_date, duration: PlanType):
    if(duration == PlanType.MONTHLY):
        return start_date+timezone.timedelta(days=30)
    elif duration == PlanType.ANNUAL:
        return start_date+timezone.timedelta(days=365)
