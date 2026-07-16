import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an AI implementation consultant.

Given

- project details
- ONE approved hypothesis

Generate ONE experiment.

Return ONLY JSON.

Schema:

{
    "title":"",
    "objective":"",
    "methodology":"",
    "required_data":"",
    "success_criteria":"",
    "failure_criteria":"",
    "decision_rule":"",
    "timeline":"",
    "owner":"",
    "risks":"",
    "fallback_plan":"",
    "status":"Proposed",

    "expert_review":{

        "agreement":"",

        "edited_title":"",

        "edited_objective":"",

        "edited_methodology":"",

        "edited_required_data":"",

        "edited_success_criteria":"",

        "edited_failure_criteria":"",

        "edited_decision_rule":"",

        "edited_timeline":"",

        "edited_owner":"",

        "edited_risks":"",

        "edited_fallback_plan":"",

        "comments":"",

        "ready":false
    }
}
"""


def generate_experiment(project, hypothesis):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Approved Hypothesis

{json.dumps(hypothesis, indent=2)}

"""

    response = generate_response(
        SYSTEM_PROMPT + prompt
    )

    try:
        return json.loads(response)

    except Exception:

        start = response.find("{")
        end = response.rfind("}") + 1

        return json.loads(response[start:end])