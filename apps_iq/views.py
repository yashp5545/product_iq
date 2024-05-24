import os
from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from .models import App, Module, Challenge, Level, LevelResponses, Categories, Skill, SkillResponses, Section, Topic, Lession, Question
from .helper import get_final_result_of_module
from users.models import User
from users.isAuth import isAuth
from users.isSubscribed import isSubscribed, is_subscribed_to_app, is_allowed
from users.referal import check_and_reward_referer

from rest_framework.decorators import api_view
from rest_framework.response import Response

from gpt.helper import get_response, get_response_worktools

MIN_LEN = 72


@api_view(['GET'])
@isAuth
def get_all(request, user):
    apps = App.objects.all()
    return Response([{
        'id': app.id,
        'app_name': app.app_name,
        'description': app.description,
        'is_subscribed': is_subscribed_to_app(app.id, user['id']),
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
    is_subscribed = is_subscribed_to_app(app_id, user['id'])
    return Response([{
        'id': module.id,
        'module_name': module.name,
        'description': module.description,
        'active': module.active,
        'order': module.order_of_display,
        'is_allowed': (not module.subscription_required) or is_subscribed,
        'complition': {
            'completed': complition[module.id][0],
            'total': complition[module.id][1]
        },
        'result': get_final_result_of_module(user, module.id)
    } for module in modules])


@api_view(['GET'])
@isAuth
def get_challenges_labels(request, user, app_id, module_id):

    if not is_allowed(Module, module_id, app_id, user['id']):
        app = App.objects.get(id=app_id)
        return Response({"error": f"You are not subscribed to {app.app_name}!"}, status=403)
    # if completed show completed and how many star rating
    challenge = Challenge.objects.filter(module_id=module_id)
    print(challenge)
    # is_subscribed = is_subscribed_to_app(app_id, user['id'])

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

    response = []

    for ch in challenge:
        nch = {}
        nch['id'] = ch.id
        nch['challenge_name'] = ch.name
        nch['description'] = ch.description
        nch['active'] = ch.active
        nch['complition'] = challenge_completed[ch.id]
        nch['labels'] = []
        is_locked = False
        for level in Level.objects.filter(challenge_id=ch.id).order_by("order_of_display"):
            nlr = LevelResponses.objects.filter(user=user['id'], level=level.id)
            nlr_exist = nlr.exists()
            nlr_first = nlr.first()
            nl = {
                'id': level.id,
                'level_name': level.name,
                'active': level.active,
                'is_locked': is_locked,
                "order": level.order_of_display,

            }

            if not is_locked:
                nl.update({
                    'level_question': level.description,
                    'completed': nlr_exist,
                    'rating': nlr_first.evalution_result if nlr_exist else None,
                    'result': nlr_first.result if nlr_exist else None,
                    'answer': nlr_first.answer if nlr_exist else None,
                })

            nch['labels'].append(nl)
            if not nlr_exist:
                is_locked = True
        response.append(nch)
    print(response)
    return Response(response)


@api_view(['POST'])
@isAuth
def get_responce(request, user, app_id, lebel_id):
    # use gpt to give responce like rating in different skills

    lebel = Level.objects.get(id=lebel_id)
    if not is_allowed(Module, lebel.challenge.module.id, app_id, user['id']):
        app = App.objects.get(id=app_id)
        return Response({"error": f"You are not subscribed to {app.app_name}!"}, status=403)
    user = User.objects.get(id=user['id'])
    if (not lebel or not request.data["answer"]):
        return Response({
            'message': 'No level or answer found'
        }, status=400)
    if (len(request.data['answer']) < MIN_LEN):
        return Response({
            "message": f"The answer should be min {MIN_LEN} char long."
        }, status=400)

    ch = lebel.challenge
    is_locked = False
    for level in Level.objects.filter(challenge_id=ch.id).order_by("order_of_display"):
        nlr = LevelResponses.objects.filter(user=user.id, level=level.id)
        nlr_exist = nlr.exists()
        if lebel.id == level.id:
            break;
        if not nlr_exist:
            is_locked = True
            break;
    if is_locked:
        return Response({"error": "Please solve all the previous question to attempt this."}, status=403)

    response = {}

    # if (os.environ.get("MODE") == "DEV"):
    #     overall_score = 0
    #     report={}
    # else:

    responce, prompt = get_response(request.data["answer"], lebel.lebel_prompt)
    if (os.environ.get("MODE") == "DEV"):
        response["prompt"] = prompt
        response["responce"] = responce

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
    print(all_responce)
    if (len(all_responce) >= 2):
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
@isAuth
def get_skills(request, user, app_id, categorie_id):
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
        'is_allowed': is_allowed(Skill, skill.id, app_id, user['id']),
        'question_suggestion': [
            {
                'id': question.id,
                'field_name': question.name,
                'placeholder': question.placeholder,
                'type': question.type,
            } for question in Question.objects.filter(skill_id=skill.id)
        ] if is_allowed(Skill, skill.id, app_id, user['id']) else None,
    } for skill in skills])


@api_view(['POST'])
@isAuth
def get_skill_responce(request, user, app_id, skill_id):
    # assuming answer is of type json and now a dict
    answer = request.data['answer']
    skill = Skill.objects.filter(id=skill_id).first()

    if (not skill):
        return Response({
            'message': 'No skill found'
        }, status=404)
    if not is_allowed(Skill, skill.id, app_id, user['id']):
        app = App.objects.get(id=app_id)
        return Response({"error": f"You are not subscribed to {app.app_name}!"}, status=403)
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
        result=result
    )
    skill_response.save()

    # send the saved response
    return Response({
        'id': skill_response.id,
        'answer': skill_response.answer,
        'result': skill_response.result
    })


@api_view(['GET'])
@isAuth
def get_sections_topics(request, user, app_id):
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
                'is_allowed': is_allowed(Topic, topic.id, app_id, user['id']),
                'id': topic.id,
                'name': topic.name,
                'active': topic.active,
            } for topic in Topic.objects.filter(section_id=section.id)
        ]
    } for section in sections])


@api_view(['GET'])
@isAuth
def get_lessions(request, user, app_id, topic_id):
    lessions = Lession.objects.filter(topic_id=topic_id)

    if (not lessions):
        return Response({
            'message': 'No lessions found'
        }, status=404)
    if not is_allowed(Topic, lessions.first().topic.id, app_id, user['id']):
        app = App.objects.get(id=app_id)
        return Response({"error": f"You are not subscribed to {app.app_name}!"}, status=403)
    return Response([{
        'id': lession.id,
        'name': lession.name,
        'description': lession.description,
        'active': lession.active,

    } for lession in lessions])


@api_view(["GET"])
@isAuth
def get_trending_topics(request, user, type):
    limit = int(request.query_params.get('limit', 5))
    if type == "modules":
        challenges = Challenge.objects.order_by("-id")[:limit]
        response = {}
        for challenge in challenges:
            module = challenge.module
            module_id = module.id
            module_name = module.name

            if module_id not in response.keys():
                response[module_id] = {}
                response[module_id]["module_id"] = module_id
                response[module_id]["module_name"] = module_name
                response[module_id]["challenges"] = []
                response[module_id]["is_allowed"] = is_allowed(
                    Module, module_id, module.app.id, user['id'])
            response[module_id]["challenges"].append({
                "challenge_name": challenge.name,
                "challenge_id": challenge.id
            })

        # return Response({
        #     "challenges": [
        #         {
        #             "id": challenge.id,
        #             "name": challenge.name,
        #             "module_id": challenge.module.id,
        #             "module_name": challenge.module.name,
        #             "is_allowed": is_allowed(Module, challenge.module.id, challenge.module.app.id, user['id'])
        #         }
        #         for challenge in challenges],
        # })
        return Response({"modules": response.values()})
    elif type == "worktools":
        skills = Skill.objects.order_by("-id")[:limit]
        response = {}
        for skill in skills:
            category = skill.category
            category_id = category.id
            category_name = category.name
            if category_id not in response.keys():
                response[category_id] = {}
                response[category_id]["category_id"] = category_id
                response[category_id]["category_name"] = category_name
                response[category_id]["skills"] = []
            response[category_id]["skills"].append({
                "skill_id": skill.id,
                "skill_name": skill.name,
            })
        return Response({"category": response.values()})

    else:
        return Response({
            "error": "only possible types are modules and worktools.",
        })
