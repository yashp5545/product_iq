from django.urls import path
from . import views


urlpatterns = [
    path('plans/get', views.get_all_plans, name="get_all_plans"),
    ## payment intent


    ## webhook integration

    
]
