import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are assisting an AI Governance implementation project.

The user has proposed a NEW hypothesis title.

Using:

- the approved project
- business objective
- existing hypotheses

Generate ONE additional hypothesis.

Do NOT repeat an existing hypothesis.

Return ONLY JSON.

Required schema:

{
    "title":"",
    "category":"",
    "priority":"Medium",
    "status":"Proposed",

    "description":"",

    "reasoning":"",

    "what_this_tests":"",

    "risk_if_wrong":"",

    "evidence_problem":"",

    "evidence_documents":"",

    "contradictions":"",

    "business_dependency":"",

    "feasibility_dependency":"",

    "risk_if_not_tested":"",

    "success_metric":"",

    "expert_review":{
        "agreement":"",
        "edited_title":"",
        "edited_description":"",
        "edited_reasoning":"",
        "edited_metric":"",
        "additional_assumption":"",
        "critical":false,
        "comments":""
    }
}
"""


def generate_manual_hypothesis(project, title, existing):

    prompt = f"""
Project

{project}

Existing hypotheses

{json.dumps(existing, indent=2)}

New hypothesis title

{title}
"""

    response = generate_response(
        SYSTEM_PROMPT + "\n\n" + prompt
    )

    try:
        return json.loads(response)

    except Exception:

        start = response.find("{")
        end = response.rfind("}") + 1

        return json.loads(response[start:end])