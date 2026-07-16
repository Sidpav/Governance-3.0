import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an Enterprise AI Infrastructure Review Board.

Generate the final infrastructure summary.

Return ONLY JSON.

{

    "deployment_recommendation":"",

    "training_requirement":"",

    "inference_requirement":"",

    "compute_estimate":"",

    "storage_estimate":"",

    "security_controls":"",

    "data_access_restrictions":"",

    "estimated_monthly_cost":""

}
"""


def generate_infrastructure_output(

    project,

    prototype_spec,

    recommendation,

    security,

):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Prototype

{json.dumps(prototype_spec, indent=2)}

Recommendation

{json.dumps(recommendation, indent=2)}

Security Review

{json.dumps(security, indent=2)}

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