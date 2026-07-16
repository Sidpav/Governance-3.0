import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT="""
You are an enterprise AI solution architect.

Generate a complete Prototype Specification.

Return ONLY JSON.

{

"architecture_design":"",

"technical_details":"",

"implementation_plan":"",

"data_features":"",

"models_used":"",

"model_validation":"",

"results_analysis":"",

"infrastructure":"",

"security":"",

"deployment":"",

"maintenance":"",

"future_scope":""

}
"""


def generate_prototype_spec(project, experiments):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Approved Experiments

{json.dumps(experiments, indent=2)}

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

        if start == -1 or end == 0:
            raise ValueError(
                f"LLM did not return JSON.\n\nResponse:\n{response}"
            )

        return json.loads(response[start:end])