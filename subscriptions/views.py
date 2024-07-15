from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view

from rest_framework.response import Response
import stripe
from django.utils import timezone

from .models import Plan, SubscriptionPayment, Coupon, PlanType, SubscriptionTrack
from users.isAuth import isAuth
from .helper import handle_checkout_session, get_end_date, get_number_of_discount, get_discounted_price, get_coupon_discount
from users.models import User
from users.isSubscribed import is_subscribed_to_app
from users.isPlanSubscribed import is_subscribed_to_plan
from apps_iq.models import App


stripe.api_key = settings.STRIPE_SECRET_KEY

FACTOR = 0.1


@api_view(['GET'])
@isAuth
def get_all_plans(request, user):
    coupon = request.query_params.get('coupon', None)
    coupon_discount = get_coupon_discount(coupon)
    if coupon_discount == -1:
        return Response({'error': 'Invalid Coupon'}, status=404)

    plans = Plan.objects.all()
    user = User.objects.get(id=user['id'])
    number_of_discount = get_number_of_discount(user)

    return Response([{
        'id': plan.id,
        'name': plan.name,
        'price_monthly': float(plan.monthly_price),
        'discounted_monthly': get_discounted_price(plan, PlanType.MONTHLY, number_of_discount, coupon_discount),
        'price_annual': float(plan.annual_price),
        'discounted_annual': get_discounted_price(plan, PlanType.FOURMONTHS, number_of_discount, coupon_discount),
        'description': plan.description,
        'recommended': plan.recommended,
        'apps': [app.app_name for app in plan.apps.all()]
    } for plan in plans])


# create payment intent || strive checkout session

@ api_view(['POST'])
@ isAuth
def create_payment_intent(request, user, plan_id, duration):
    coupon = request.query_params.get('coupon', None)
    coupon_discount = get_coupon_discount(coupon)
    if coupon_discount == -1:
        return Response({'error': 'Invalid Coupon'}, status=404)

    if not request.data['address']:
        Response({
            "error": "Please provide address!"
        }, status=404)

    plan = Plan.objects.filter(id=plan_id).first()

    print(plan)

    if not plan:
        return Response({'error': 'Invalid Plan'}, status=404)

    if (duration not in [plan_duration.value for plan_duration in PlanType]):
        return Response({'error': "Duration must be "+"/".join([plan_duration.value for plan_duration in PlanType])}, status=404)

    user = User.objects.get(id=user['id'])
    number_of_discount = get_number_of_discount(user)
    plan_price = plan.annual_price if duration == PlanType.FOURMONTHS else plan.monthly_price

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
            "user_id": user.id,
            "plan_id": plan.id,
            "subscription_track_id": subscription_track.id,
            "amount": plan_price, 
            "number_of_discount_to_reduce": number_of_discount,
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
    # if event['type'] == 'payment_intent.succeeded':
    #     print("payment_intent.succeeded: ", event)
    #     session = event['data']['object']
    #     handle_checkout_session(session)
    if event['type'] == 'checkout.session.completed':
        print(event, "checkout.session.completed")
        session = event['data']['object']
        handle_checkout_session(session)
    # if event['type'] == ''

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
        'actual_amount': subscription.plan.annual_price if subscription.duration == PlanType.FOURMONTHS else subscription.plan.monthly_price,
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


@api_view(["GET"])
@isAuth
def current_access_status(request, user):
    app_details = []
    all_apps = App.objects.filter()
    for app in all_apps:
        app_detail = {}
        app_detail["id"] = app.id
        app_detail["name"] = app.app_name
        app_detail["is_subscribed"] = is_subscribed_to_app(app.id, user['id'])
        app_details.append(app_detail)
    
    plan_details = []
    all_plans = Plan.objects.filter()
    for plan in all_plans:
        print(plan)
        plan_detail = {}
        plan_detail["id"] = plan.id
        plan_detail["name"] = plan.name
        plan_detail["is_subscribed"] = is_subscribed_to_plan(plan.id, user['id'])
        plan_details.append(plan_detail)
    print(app_details)
    return Response({
        "planDetails": plan_details,
        "app_details": app_details
    })