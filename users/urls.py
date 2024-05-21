from django.urls import path, include
from . import views


urlpatterns = [
    path('auth/login', views.login, name="login"),
    path('auth/register', views.register, name="register"),
    path('auth/user', views.get_user, name="user"),
    path('auth/refresh', views.refress_token, name="refresh"),
    path('auth/logout', views.logout, name="logout"),
    path('user/update', views.update_user, name="update_user"),
    path('user/add/referredby', views.add_referred_by, name='add_referred_by'),
    path('user/action/', include('django.contrib.auth.urls')),
    path('user/enum/experience', views.get_product_exp_types, name="get_product_exp_types")
]
