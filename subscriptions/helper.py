from users.models import User
from .models import Plan

def handle_checkout_session(session):
    user = User.objects.get(id=session.metadata['user_id'])
    plan = Plan.objects.get(id=session.metadata['plan_id'])
    plan.subscribe(user)
    return True