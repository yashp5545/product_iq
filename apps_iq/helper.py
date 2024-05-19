from.models import Challenge, Level, LevelResponses

def get_final_result_of_module(user: dict, module_id: int):
    challenges = Challenge.objects.filter(module_id=module_id)
    for challenge in challenges:
        levels = Level.objects.filter(challenge_id=challenge.id)
        for level in levels:
            if not LevelResponses.objects.filter(user=user['id'], level=level.id):
                return False
    return True
    # responce = {}
    # for challenge in challenges:
    #     levels = Level.objects.filter(challenge_id=challenge.id)
    #     for level in levels:
    #         responce[level.description] = LevelResponses.objects.get(user=user['id'], level=level.id).answer
    # return responce
