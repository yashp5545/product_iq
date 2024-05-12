import os
from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from .models import App, Module, Challenge, Level, LevelResponses, Categories, Skill, SkillResponses, Section, Topic, Lession, Question
from .helper import get_final_result_of_module
from users.models import User
from users.isAuth import isAuth
from users.referal import check_and_reward_referer

from rest_framework.decorators import api_view
from rest_framework.response import Response

from gpt.helper import get_response, get_response_worktools

MIN_LEN = 72

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
            'level_question': level.description,
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
    # use gpt to give responce like rating in different skills
    lebel = Level.objects.get(id=lebel_id)
    user = User.objects.get(id=user['id'])
    if (not lebel or not request.data["answer"]):
        return Response({
            'message': 'No level or answer found'
        }, status=400)
    if (len(request.data['answer']) < MIN_LEN):
        return Response({
            "message": f"The answer should be min {MIN_LEN} char long."
        }, status=400)
    response = {}

    # if (os.environ.get("MODE") == "DEV"):
    #     overall_score = 0
    #     report={}
    # else:
    responce = get_response(request.data["answer"], lebel.lebel_prompt)
    overall_score = responce['overall_score'] if 'overall_score' in responce else 0
    report = responce['report'] if 'report' in responce else {}

    lebel_response = LevelResponses.objects.create(
        user=user,
        level=lebel,
        answer=request.data["answer"],
        evalution_result=overall_score,
        result=report,
    )
    lebel_response.save()

    # return last two lebel_respose

    response.update(
        {
            'now': {
                'answer': lebel_response.answer,
                'result': lebel_response.result,
                'evaluation_result': lebel_response.evalution_result
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
    # if (os.environ.get("MODE") == "DEV"):
    #     print(f"{response=}")
    #     # add the gpt output to the response
    #     response.update({
    #         'gpt_output': responce
    #     })
    check_and_reward_referer(user)
    return Response(response)


@api_view(['GET'])
def search(request, search):
    search_term = search.lower()
    pattern = search_term
    query = Q(name__iregex=pattern) | Q(description__iregex=pattern)
    query_name = Q(name__iregex=pattern)
    result = {}

    search_lebel_query = request.GET.get('search_lebel', None)
    depth_query = request.GET.get('depth', None)
    if (depth_query is None):
        depth_query = 5
    else:
        depth_query = int(depth_query)
    if not search_lebel_query:
        depth_query = 20
    print(depth_query)

    if search_lebel_query == "module" or not search_lebel_query:
        if depth_query > 0:
            modules = Module.objects.filter(query)
            if (modules):
                result['modules'] = [{
                    'id': module.id,
                    'module_name': module.name,
                    'description': module.description,
                    'active': module.active,
                } for module in modules]
            depth_query -= 1
        if depth_query > 0:
            challenges = Challenge.objects.filter(query)
            if (challenges):
                result['challenges'] = [{
                    'id': challenge.id,
                    'challenge_name': challenge.name,
                    'description': challenge.description,
                    'active': challenge.active,
                    'module': challenge.module.id,
                    'module_name': challenge.module.name,
                } for challenge in challenges]
            depth_query -= 1
        if depth_query > 0:
            labels = Level.objects.filter(query)
            if (labels):
                result['labels'] = [{
                    'id': label.id,
                    'label_name': label.name,
                    'level_question': label.description,
                    'active': label.active,
                    'challenge': label.challenge.id,
                    'challenge_name': label.challenge.name,
                    'module': label.challenge.module.id,
                    'module_name': label.challenge.module.name,
                } for label in labels]
            depth_query -= 1
    if search_lebel_query == "categorie" or not search_lebel_query:
        print("hi")
        if depth_query > 0:
            categories = Categories.objects.filter(query)
            if (categories):
                result['categories'] = [{
                    'id': categorie.id,
                    'name': categorie.name,
                    'description': categorie.description,
                    'active': categorie.active,
                } for categorie in categories]
            depth_query -= 1
        if depth_query > 0:
            skills = Skill.objects.filter(query)
            if (skills):
                result['skills'] = [{
                    'id': skill.id,
                    'name': skill.name,
                    'description': skill.description,
                    'active': skill.active,
                    'categorie': skill.category.id,
                    'categorie_name': skill.category.name,
                } for skill in skills]
            depth_query -= 1
    if search_lebel_query == "section" or not search_lebel_query:
        if depth_query > 0:
            sections = Section.objects.filter(query_name)
            if (sections):
                result['sections'] = [{
                    'id': section.id,
                    'name': section.name,
                    'active': section.active,
                    'app': section.app.id,
                } for section in sections]
            depth_query -= 1
        if (depth_query > 0):
            topic = Topic.objects.filter(query_name)
            if (topic):
                result['topics'] = [{
                    'id': topic.id,
                    'name': topic.name,
                    'active': topic.active,
                    'section': topic.section.id,
                    'section_name': topic.section.name,
                } for topic in topic]
            depth_query -= 1
        if depth_query > 0:
            lessions = Lession.objects.filter(query)
            if (lessions):
                result['lessions'] = [{
                    'id': lession.id,
                    'name': lession.name,
                    'description': lession.description,
                    'active': lession.active,
                    'topic': lession.topic.id,
                    'topic_name': lession.topic.name,
                    'section': lession.topic.section.id,
                    'section_name': lession.topic.section.name,
                } for lession in lessions]
            depth_query -= 1

    return Response(result, status=200)


@api_view(['GET'])
def get_categories(request, app_id):
    categories = Categories.objects.filter(app_id=app_id)
    if (not categories):
        return Response({
            'message': 'No categories found'
        }, status=404)
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
        }, status=404)
    return Response([{
        'id': skill.id,
        'name': skill.name,
        'description': skill.description,
        'active': skill.active,
        'tags': skill.tags,
        'question_suggestion': [
            {
                'id': question.id,
                'field_name': question.name,
                'placeholder': question.placeholder,
                'type': question.type,
            } for question in Question.objects.filter(skill_id=skill.id)
        ],
    } for skill in skills])


@api_view(['POST'])
@isAuth
def get_skill_responce(request, user, skill_id):
    answer = request.data['answer'];                          # assuming answer is of type json and now a dict
    skill = Skill.objects.filter(id=skill_id).first()
    if (not skill):
        return Response({
            'message': 'No skill found'
        }, status=404)
    user = User.objects.get(id=user['id'])

    result = None
    try:
        result = get_response_worktools(answer)
    except:
        return Response({"error": "Error generating evaluation!"}, status=500)

    skill_response = SkillResponses.objects.create(
        user=user,
        skill=skill,
        answer=request.data['answer'],
        result= result
    )
    skill_response.save()

    # send the saved response
    return Response({
        'id': skill_response.id,
        'answer': skill_response.answer,
        'result': skill_response.result
    })


@api_view(['GET'])
def get_sections_topics(request, app_id):
    sections = Section.objects.filter(app_id=app_id)
    if (not sections):
        return Response({
            'message': 'No sections found'
        }, status=404)
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
        }, status=404)
    return Response([{
        'id': lession.id,
        'name': lession.name,
        'description': lession.description,
        'active': lession.active,

    } for lession in lessions])
