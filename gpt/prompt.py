common_promp_1 = '''Reply in json format {"overall_score":"", report: {names: [""], scores: [""], suggestions_report:[""] }, focus_area: "", corrected:"" } where overall_score is out of 10, report json attribute consists of the score by attributes used, suggestions by attribute, and suggestion for each attribute. Focus areas will have the areas to focus on to improve the score and corrected attribute will only have the corrected answer without suggestion, with the maximum score for below as a product coach in commanding tone for professional that should focus on product mindset.'''
common_prompt_3 = """Score out of 10: {"____"}. Mention the attributes to measure the score and suggestions for each attribute to improve the score and a corrected answer to have the maximum score."""


def get_prompt_for_lebel(ans: str, context_prompt_2: str) -> str:
    prompt: str = ""
    prompt += common_promp_1+"\n\n"
    prompt += context_prompt_2+"\n\n"
    prompt += common_prompt_3.replace("____", ans)
    return prompt


test_input = {
    "Main problem": "Users aren't adopting our product once they sign up", 
    "High-level solution": " An onboarding flow that introduces users to our product", 
    "Features": "A step-by-step walkthrough of how to use the product", 
    "How you'll measure success": "Increase new user activation by 15%", 
    "Launch date": "July 15th"
}
common_promp_product_worktools = ''' Reply in json format {"prd_title":"", prd_category":"",prd_tags”:””, prd_content: {problem_statement:””, objective: “”, persona: “”, risks_assumptions: “”, high_level_solution: “”, features_list: [{feature_name: “”, feature_detail_points”:[“”]}]}, success_metrics: “”}
 where pro title is the overall prd name or product name, prd_category is the industry sub-category name, prd_tags are the various tags related to the problem, persona is the archetype of the user with pain point of the persona, risks_assumptions are the challenges or subsequent issues that can arise, high_level_solution is the overall solution chose to solve the problem, features_list consist of the list of features that are must-haves and creative ways with well defined details points in feature_detail_points and success_metrics lists the various metrics grouped by aarrr pirate funnel, engagement metrics that can be used to measure the success of the features


 Write a well-defined and detailed product requirement document as a Principal Product Manager with precise articulation and strong product mindset. Considering'''
def get_prompt_for_worktools(input: dict[str, str]) -> str:
    prompt = common_promp_product_worktools
    for key, values in input.items():
        prompt+= f" {key} as {values}."
    prompt+="\n"
    return prompt


if __name__ == "__main__":
    print(get_prompt_for_worktools(test_input))