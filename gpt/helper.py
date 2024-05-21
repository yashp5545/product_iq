import json
from gpt.prompt import get_prompt_for_lebel, get_prompt_for_worktools
from gpt.api import openai

def clean_code(code: str, template: str)->dict:
    clean_code = code.replace(f"```{template}", "").replace("```", "").strip()
    return json.loads(clean_code)


def get_response(ans:str, lebel_prompt)->dict:
    prompt = get_prompt_for_lebel(ans, lebel_prompt)
    print(f"{prompt=}")
    code = openai(prompt, "_")
    return clean_code(code, "json"), prompt

def get_response_worktools(answer: dict[str, str]):
    prompt = get_prompt_for_worktools(answer)
    print(f"{prompt=}")
    code = openai(prompt, '-_')
    return clean_code(code, "json")