from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('all', views.get_all, name="get_all"),
    path('<int:app_id>/module', views.get_modules, name="get_modules"),
    path('<int:app_id>/module/<int:module_id>',
         views.get_challenges_labels, name="get_challenges_labels"),
    path('<int:app_id>/response/lebel/<int:lebel_id>', views.get_responce, name="get_responce"),
    path('<int:app_id>/response/lebel/<int:lebel_id>/all', views.get_all_previous_answers, name="get_all_previous_answers"),


    path('<int:app_id>/categorie', views.get_categories, name="get_categories"),
    path('<int:app_id>/categorie/<int:categorie_id>',
         views.get_skills, name="get_skills"),
    path('<int:app_id>/response/skill/<int:skill_id>', views.get_skill_responce, name="get_skill_responce"),


     path('<int:app_id>/section/topics', views.get_sections_topics, name="get_sections_topics"),
     path('<int:app_id>/section/topics/<int:topic_id>/lessions',
               views.get_lessions, name="get_lessions"),

     path('search/<str:search>', views.search, name="search"),

     path('trending/<str:type>', views.get_trending_topics, name = "get_trending_topics"),
     
     #######################3
     # path('appcreate',views.createAppFun,name="createappPage")
     

]
