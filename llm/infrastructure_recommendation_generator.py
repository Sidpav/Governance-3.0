import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are a Senior AI Infrastructure Architect.

You are given:

- Business Problem
- Approved Hypotheses
- Approved Experiments
- Prototype Specification
- Infrastructure Decisions

Recommend the infrastructure.

Return ONLY JSON.

{
    "recommendations":[
        {
            "area":"",
            "recommendation":"",
            "reason":""
        }
    ]
}
"""


def generate_infrastructure_recommendation(

    project,

    hypotheses,

    experiments,

    prototype_spec,

    review,

):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Hypotheses

{json.dumps(hypotheses, indent=2)}

Experiments

{json.dumps(experiments, indent=2)}

Prototype

{json.dumps(prototype_spec, indent=2)}

Infrastructure Decisions

{json.dumps(review, indent=2)}

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