from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('all', views.get_all, name="get_all"),
    path('<int:app_id>', views.get_modules, name="get_modules"),
    path('<int:app_id>/module/<int:module_id>',
         views.get_challenges_labels, name="get_challenges_labels"),
    path('response/lebel/<int:lebel_id>', views.get_responce, name="get_responce"),

]
