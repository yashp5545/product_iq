from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view

from rest_framework.response import Response
import stripe
from django.utils import timezone

from .models import Plan, SubscriptionPayment, Coupon, PlanType
from users.isAuth import isAuth
from .helper import handle_checkout_session
from users.models import User


stripe.api_key = settings.STRIPE_SECRET_KEY

FACTOR = 0.1


@api_view(['GET'])
@isAuth
def get_all_plans(request, user):
    coupon = request.query_params.get('coupon', None)
    coupon_discount = 0
    if coupon:
        coupon = Coupon.objects.filter(code=coupon).first()
        if not coupon:
            return Response({'error': 'Invalid Coupon'}, status=404)
        coupon_discount = float(coupon.discount_in_decimal)
    plans = Plan.objects.all()
    user = User.objects.get(id=user['id'])
    number_of_discount = user.number_of_discounts
    if (number_of_discount > 10):
        number_of_discount = (10)

    return Response([{
        'id': plan.id,
        'name': plan.name,
        'price_monthly': float(plan.monthly_price),
        'discounted_monthly': max(float(plan.monthly_price)
                                  - (float(plan.monthly_price) *
                                     (number_of_discount * FACTOR))
                                  - (float(plan.monthly_price) * coupon_discount), 0),
        'price_annual': float(plan.annual_price),
        'discoutned_annual': max(float(plan.annual_price)
                                 - (float(plan.annual_price)
                                    * number_of_discount * FACTOR)
                                 - (float(plan.annual_price) * coupon_discount), 0),
        'description': plan.description,
        'recommended': plan.recommended,
        'apps': [app.app_name for app in plan.apps.all()]
    } for plan in plans])


# create payment intent || strive checkout session

@ api_view(['POST'])
@ isAuth
def create_payment_intent(request, user: dict, plan_id, duration):
    plan = Plan.objects.filter(id=plan_id).first()
    print(plan)

    if not plan:
        return Response({'error': 'Invalid Plan'}, status=404)

    if (duration not in [plan_duration.value for plan_duration in PlanType]):
        return Response({'error': "Duration must be "+"/".join([plan_duration.value for plan_duration in PlanType])}, status=404)

    plan_price = plan.annual_price if duration == PlanType.ANNUAL else plan.monthly_price

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': plan.name,
                    'description': plan.description,

                },
                'unit_amount': plan_price * 100,
            },
            'quantity': 1,
        }],
        metadata={
            'user_id': user['id'],
            'plan_id': plan_id,
        },
        mode='payment',
        success_url=settings.PAYMENT_SUCCESS_URL,
        cancel_url=settings.PAYMENT_CANCEL_URL,
    )
    print("hello")
    print(checkout_session)
    print("bye")

    # return Response("success");

    return Response({
        'id': checkout_session.id,
        'payment_intent': checkout_session.payment_intent,
        'client_secret': checkout_session.client_secret,
    })


# webhook implementation

@ api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return Response({'error': e}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': e}, status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        handle_checkout_session(session)

    return Response({'status': 'success'}, status=200)


@api_view(["GET"])
@isAuth
def get_my_subscriptions(request, user):
    user = User.objects.get(id=user['id'])
    subscriptions = SubscriptionPayment.objects.filter(user=user)
    return Response([{
        'plan': subscription.plan.name,
        'start_date': subscription.start_date,
        'is_valid': subscription.end_date >= timezone.now().date(),
        'end_date': subscription.end_date,
        'duration': subscription.duration,
        'amount_paid': subscription.amount,
        'actual_amount': subscription.plan.annual_price if subscription.duration == PlanType.ANNUAL else subscription.plan.monthly_price,
        'apps_subscribed_to': [
            {
                'id': app.id,
                'name': app.app_name,
                'description': app.description,
            } for app in subscription.plan.apps.all()
        ]
    } for subscription in subscriptions])
