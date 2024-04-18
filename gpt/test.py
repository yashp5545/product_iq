output = '''```json
{
  "overall_score": "7",
  "report": {
    "names": ["Grammar", "Clarity", "Specificity", "Logical flow", "Potential impact"],
    "scores": ["6", "7", "6", "7", "8"],
    "suggestions_report": [
      "Watch out for minor grammar errors, proofread thoroughly.",
      "Ensure the statement is crystal clear, avoid jargon or ambiguous language.",
      "Provide more specific details to enhance understanding.",
      "Ensure the flow of ideas is smooth and coherent.",
      "Highlight the potential impact of the problem statement more explicitly."
    ]
  },
  "focus_area": "Focus on improving clarity and specificity to ensure the problem statement is easily understandable and actionable. Additionally, work on highlighting the potential impact of the problem statement more effectively.",
  "corrected": "There is a plethora of tools available for product roadmap planning and OKRs alignment. However, there is a noticeable gap when it comes to tools that specifically cater to defining a product-driven approach. This absence hampers the effective implementation of OKRs within a product-centric framework, hindering teams from aligning their objectives with the overarching product strategy."
}
```'''

from helper import clean_code

print(clean_code(output, "json")["report"]["names"])