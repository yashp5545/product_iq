from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view

from rest_framework.response import Response

import stripe

from .models import Plan
from users.isAuth import isAuth
from .helper import handle_checkout_session

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['GET'])
def get_all_plans(request):
    plans = Plan.objects.all()

    return Response([{
        'id': plan.id,
        'name': plan.name,
        'price_monthly': plan.price_monthly,
        'price_annual': plan.price_annual,
        'description': plan.description,
        'recommended': plan.recommended,
        'apps': [app.app_name for app in plan.apps.all()]
    } for plan in plans])


# create payment intent || strive checkout session

@api_view(['POST'])
@isAuth
def create_payment_intent(request, user: dict, plan_id):
    plan = Plan.objects.get(id=plan_id)

    if not plan:
        return Response({'error': 'Invalid Plan'}, status=404)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': plan.name,
                    'description': plan.description,

                },
                'unit_amount': plan.price * 100,
            },
            'quantity': 1,
        }],
        metadata={
            'user_id': user['id'],
            'plan_id': plan_id,
        },  
        mode='payment',
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    return Response({
        'id': checkout_session.id,
        'payment_intent': checkout_session.payment_intent,
        'client_secret': checkout_session.client_secret,
    })


# webhook implementation

@api_view(['POST'])
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
