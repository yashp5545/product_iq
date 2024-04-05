from django.shortcuts import render
from rest_framework.decorators import api_view

from rest_framework.response import Response

from .models import Plan


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


## create payment intent

## webhook implementation