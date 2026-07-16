import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an AI Governance Board.

You are given:

• Prototype Specification
• Stakeholder Review Summaries

Produce a final consolidated governance review.

Return ONLY valid JSON.

{

    "feedback_summary":"",

    "agreement_areas":[
        ""
    ],

    "disagreement_areas":[
        ""
    ],

    "feature_changes_required":[
        ""
    ],

    "risks_raised":[
        ""
    ],

    "recommended_mvp_scope":""

}

Do not return markdown.
Do not explain.
Return JSON only.
"""

def generate_feedback_summary(

    project,

    prototype_spec,

    stakeholder_summaries,

):

    prompt = f"""

Project

{json.dumps(project,indent=2)}

Prototype Specification

{json.dumps(prototype_spec,indent=2)}

Stakeholder Reviews

{json.dumps(stakeholder_summaries,indent=2)}

"""

    response = generate_response(

        SYSTEM_PROMPT + prompt

    )

    print(response)

    try:

        return json.loads(response)

    except Exception:

        start = response.find("{")

        end = response.rfind("}") + 1

        return json.loads(

            response[start:end]

        )