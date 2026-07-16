import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an AI Governance Review Board.

You are given

- Project
- Prototype Specification
- Stakeholder Role
- Stakeholder Answers

Write a concise stakeholder review summary.

Return ONLY valid JSON.

{
    "product_view":"",
    "data_view":"",
    "compliance_view":"",
    "business_view":"",
    "infrastructure_view":"",
    "overall_decision":"",
    "mvp_recommendation":"",
    "blockers":"",
    "confidence":""
}
"""


def generate_stakeholder_summary(
    project,
    prototype_spec,
    stakeholder_role,
    review,
):

    prompt = f"""

Project

{json.dumps(project,indent=2)}

Prototype Specification

{json.dumps(prototype_spec,indent=2)}

Stakeholder

{stakeholder_role}

Review

{json.dumps(review,indent=2)}

"""

    response = generate_response(
        SYSTEM_PROMPT + prompt
    )

    try:
        return json.loads(response)

    except Exception:

        start=response.find("{")
        end=response.rfind("}")+1

        return json.loads(response[start:end])