from django.shortcuts import render

# Create your views here.

from .models import App, Module, Challenge, Level, LevelResponses

from users.models import User
from users.isAuth import isAuth

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def get_all(request):
    apps = App.objects.all()
    return Response([{
        'id': app.id,
        'app_name': app.app_name,
        'description': app.description,
    } for app in apps])


@api_view(['GET'])
def get_modules(request, app_id):
    modules = Module.objects.filter(app_id=app_id)
    return Response([{
        'id': module.id,
        'module_name': module.name,
        'description': module.description,
    } for module in modules])


@api_view(['GET'])
def get_challenges_labels(request, app_id, module_id):
    # if completed show completed and how many star rating
    challenge = Challenge.objects.filter(module_id=module_id)
    return Response([{
        'id': challenge.id,
        'challenge_name': challenge.name,
        'description': challenge.description,
        'labels': [{
            'id': level.id,
            'level_name': level.name,
            'description': level.description,
            'active': level.active,
        } for level in Level.objects.filter(challenge_id=challenge.id)]
    } for challenge in challenge])


@api_view(['POST'])
@isAuth
def get_responce(request, user, lebel_id):
    # use gpt to give responce like ratiting in different skills

    lebel = Level.objects.get(id=lebel_id)
    user = User.objects.get(id=user['id'])
    lebel_response = LevelResponses.objects.create(
        user=user,
        level=lebel,
        answer=request.data['answer'],
        evalution_result=0,
        result={}
    )
    lebel_response.save()

    # return last two lebel_respose
    response = {}
    response.update(
        {
            'now': {
                'answer': lebel_response.answer,
                'result': lebel_response.result,
                'evalution_result': lebel_response.evalution_result
            }
        })
    

    all_responce = LevelResponses.objects.filter(user=user, level=lebel)
    if (len(all_responce) > 2):
        response.update({
            'previous': {
                'answer': all_responce[len(all_responce)-2].answer,
                'result': all_responce[len(all_responce)-2].result,
                'evalution_result': all_responce[len(all_responce)-2].evalution_result,
            }
        })


    return Response(response)
