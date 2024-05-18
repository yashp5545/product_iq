from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view

from rest_framework.response import Response
import stripe
from django.utils import timezone

from .models import Plan, SubscriptionPayment, Coupon, PlanType, SubscriptionTrack
from users.isAuth import isAuth
from .helper import handle_checkout_session, get_end_date
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
def create_payment_intent(request, user, plan_id, duration):
    if not request.data['address']:
        Response({
            "error": "Please provide address!"
        })
    plan = Plan.objects.filter(id=plan_id).first()

    print(plan)

    if not plan:
        return Response({'error': 'Invalid Plan'}, status=404)

    if (duration not in [plan_duration.value for plan_duration in PlanType]):
        return Response({'error': "Duration must be "+"/".join([plan_duration.value for plan_duration in PlanType])}, status=404)

    user = User.objects.get(id=user['id'])
    plan_price = plan.annual_price if duration == PlanType.ANNUAL else plan.monthly_price

    subscription_track = SubscriptionTrack.objects.create(
        user=user,
        plan=plan,
        amount=plan_price,
        duration=duration,
    )

    customer = stripe.Customer.create(
        name=user.name,
        email=user.email,
        address=request.data['address']
    )
    # ephemeral_key = stripe.EphemeralKey.create(customer = customer.id, stripe_version= "2023-10-16")

    # payment_intent = stripe.PaymentIntent.create(
    #     amount=int(plan_price*100),
    #     currency='inr',
    #     customer=customer.id,
    #     description="ProductIQ payment service",
    #     metadata={
    #         "user_id": user.id,
    #         "plan_id": plan.id,
    #         "ephemeral_key": ephemeral_key,
    #         "customer_id": customer.id,
    #         "subscription_track_id": subscription_track.id,
    #         "amount": plan_price
    #     }
    # )

    # return Response({
    #     "payment_intent": payment_intent,
    #     "ephemeral_key": ephemeral_key,
    #     "customer": customer.id,
    #     "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
    # })
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        customer=customer['id'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': plan.name,
                    'description': plan.description,
                },
                'unit_amount': int(plan_price * 100),
            },
            'quantity': 1,
        }],
        metadata={
            'user_id': user.id,
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

    return Response(checkout_session)


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
    print(event)
    if event['type'] == 'payment_intent.succeeded':
        print(event)
        session = event['data']['object']

        # Fulfill the purchase...
        # handle_checkout_session(session)

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


@api_view(["GET"])
def success(request):
    return Response({
        "message": "success",
    }, status=201)


@api_view(["GET"])
def failed(request):
    return Response({
        "message": "failed",
    }, status=401)
