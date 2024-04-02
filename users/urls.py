from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('user', views.get_user, name="user"),
    path('refresh', views.refress_token, name="refresh"),
    path('logout', views.logout, name="logout")
]
