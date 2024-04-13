from django.shortcuts import render

# Create your views here.

from .models import App, Module, Challenge, Level, LevelResponses, Categories, Skill, SkillResponses, Section, Topic, Lession
from .helper import get_final_result_of_module
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
@isAuth
def get_modules(request, user, app_id):
    modules = Module.objects.filter(app_id=app_id)

    complition = {}

    for module in modules:
        # check how many challenges are complitely completed
        challenges = Challenge.objects.filter(module_id=module.id)
        total_challenge = len(challenges)

        challenges_completed = 0
        for ch in challenges:
            levels = Level.objects.filter(challenge_id=ch.id)
            is_level_completed = True
            for level in levels:
                if not LevelResponses.objects.filter(user=user['id'], level=level.id):
                    is_level_completed = False
                    break
            if is_level_completed:
                # print(levels)
                challenges_completed += 1

        complition[module.id] = [challenges_completed, total_challenge]

    return Response([{
        'id': module.id,
        'module_name': module.name,
        'description': module.description,
        'active': module.active,
        'complition': {
            'completed': complition[module.id][0],
            'total': complition[module.id][1]
        },
        'result': get_final_result_of_module(user, module.id)
    } for module in modules])


@api_view(['GET'])
@isAuth
def get_challenges_labels(request, user, app_id, module_id):
    # if completed show completed and how many star rating
    challenge = Challenge.objects.filter(module_id=module_id)

    challenge_completed = {}
    for ch in challenge:
        levels = Level.objects.filter(challenge_id=ch.id)
        lebel_complition_status = {
            'completed': 0,
            'total': len(levels)
        }
        for level in levels:
            if LevelResponses.objects.filter(user=user['id'], level=level.id).exists():
                lebel_complition_status['completed'] += 1
        challenge_completed[ch.id] = lebel_complition_status

    return Response([{
        'id': challenge.id,
        'challenge_name': challenge.name,
        'description': challenge.description,
        'active': challenge.active,
        'complition': challenge_completed[challenge.id],
        'labels': [{
            'id': level.id,
            'level_name': level.name,
            'description': level.description,
            'active': level.active,
            'completed': LevelResponses.objects.filter(user=user['id'], level=level.id).exists(),
            'rating': LevelResponses.objects.filter(user=user['id'], level=level.id).first().evalution_result if LevelResponses.objects.filter(user=user['id'], level=level.id).exists() else None,
            'result': LevelResponses.objects.filter(user=user['id'], level=level.id).first().result if LevelResponses.objects.filter(user=user['id'], level=level.id).exists() else None,
            'answer': LevelResponses.objects.filter(user=user['id'], level=level.id).first().answer if LevelResponses.objects.filter(user=user['id'], level=level.id).exists() else None,
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


@api_view(['GET'])
def get_categories(request, app_id):
    categories = Categories.objects.filter(app_id=app_id)
    if (not categories):
        return Response({
            'message': 'No categories found'
        })
    return Response([{
        'id': category.id,
        'name': category.name,
        # 'description': category.description,
        'active': category.active,
    } for category in categories])


@api_view(['GET'])
def get_skills(request, app_id, categorie_id):
    skills = Skill.objects.filter(category_id=categorie_id)
    if (not skills):
        return Response({
            'message': 'No skills found'
        })
    return Response([{
        'id': skill.id,
        'name': skill.name,
        'description': skill.description,
        'active': skill.active,
        'tags': skill.tags,
        'question_suggestion': skill.question_suggestion,
        'skill_prompt': skill.skill_prompt,
    } for skill in skills])


@api_view(['POST'])
@isAuth
def get_skill_responce(request, user, skill_id):
    skill = Skill.objects.get(id=skill_id)
    if (not skill):
        return Response({
            'message': 'No skill found'
        })
    user = User.objects.get(id=user['id'])
    skill_response = SkillResponses.objects.create(
        user=user,
        skill=skill,
        answer=request.data['answer'],
    )
    skill_response.save()

    # send the saved response
    return Response({
        'id': skill_response.id,
        'answer': skill_response.answer,
        'skill': skill_response.skill.id,
        'user': skill_response.user.id,
    })


@api_view(['GET'])
def get_sections_topics(request, app_id):
    sections = Section.objects.filter(app_id=app_id)
    if (not sections):
        return Response({
            'message': 'No sections found'
        })
    return Response([{
        'id': section.id,
        'name': section.name,
        'active': section.active,
        'topic': [
            {
                'id': topic.id,
                'name': topic.name,
                'active': topic.active,
            } for topic in Topic.objects.filter(section_id=section.id)
        ]
    } for section in sections])


@api_view(['GET'])
def get_lessions(request, app_id, topic_id):
    lessions = Lession.objects.filter(topic_id=topic_id)
    if (not lessions):
        return Response({
            'message': 'No lessions found'
        })
    return Response([{
        'id': lession.id,
        'name': lession.name,
        'description': lession.description,
        'active': lession.active,

    } for lession in lessions])
