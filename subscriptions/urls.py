from django.urls import path
from . import views


urlpatterns = [
    path('plans', views.get_all_plans, name="get_all_plans"),
    # payment intent

    path('payment-intent/plan/<int:plan_id>/duration/<str:duration>',
         views.create_payment_intent, name='create_payment_intent'),


    # webhook integration
    path('webhook', views.stripe_webhook, name='stripe_webhook'),

    path('my', views.get_my_subscriptions, name='get_my_subscriptions'),

    path("success", views.success, name="success"),
    path("failed", views.failed, name="failed"),
    path('details', views.current_access_status),
]
