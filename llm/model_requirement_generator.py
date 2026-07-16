import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are a Senior AI Architect.

Based on the project, data requirements and prototype specification,
recommend suitable AI models.

For every recommendation include:

- name
- type
- reason

Return ONLY JSON.

{
    "models":[
        {
            "name":"",
            "type":"",
            "reason":""
        }
    ]
}
"""


def generate_model_requirements(

    project,

    prototype_spec,

    data_requirements,

):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Prototype

{json.dumps(prototype_spec, indent=2)}

Data

{json.dumps(data_requirements, indent=2)}

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