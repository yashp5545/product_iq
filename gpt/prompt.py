common_promp_1 = '''Reply in json format {"overall_score":"", report: {names: [""], scores: [""], suggestions_report:[""] }, focus_area: "", corrected:"" } where overall_score is out of 10, report json attribute consists of the score by attributes used, suggestions by attribute, and suggestion for each attribute. Focus areas will have the areas to focus on to improve the score and corrected attribute will only have the corrected answer without suggestion, with the maximum score for below as a product coach in commanding tone for professional that should focus on product mindset.'''
common_prompt_3 = """Score out of 10: {"____"}. Mention the attributes to measure the score and suggestions for each attribute to improve the score and a corrected answer to have the maximum score."""

def get_prompt_for_lebel(ans: str, context_prompt_2:str) -> str:
    prompt: str = ""
    prompt+=common_promp_1+"\n\n"
    prompt+=context_prompt_2+"\n\n"
    prompt+=common_prompt_3.replace("____", ans)
    return prompt

