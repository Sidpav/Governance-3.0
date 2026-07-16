import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are a Senior Enterprise AI Architect.

Based on the project, generate the data requirements needed for building the AI system.

Return ONLY valid JSON.

{
    "structured_data":[
        {
            "group":"Customer Profile",
            "color":"blue",
            "categories":[
                {
                    "name":"Identity & Account",
                    "attributes":[
                        "Customer master data",
                        "Account owner"
                    ]
                }
            ]
        }
    ],

    "unstructured_data":[
        {
            "group":"Customer Communications",
            "color":"blue",
            "categories":[
                {
                    "name":"Direct Contact",
                    "sources":[
                        "Customer emails",
                        "Meeting transcripts"
                    ]
                }
            ]
        }
    ],

    "data_leakage_questions":[
        ""
    ],

    "data_quality_questions":[
        ""
    ],

    "topic_coverage":[
        ""
    ],

    "model_recommendations":[
        {
            "name":"XGBoost",
            "type":"ML",
            "reason":""
        }
    ]
}

Rules

Generate the data specifically for THIS project.

Do NOT hardcode churn examples.

Generate:

• 4-8 structured groups
• 2-5 categories per group
• 2-6 attributes per category

Generate:

• 4-6 unstructured groups
• realistic data sources

Generate:

• 8-12 data leakage questions

Generate:

• 8-12 data quality questions

Generate:

• 8-15 topic coverage items

Generate:

• Appropriate ML / AI / LLM models for this project.

Return JSON only.
"""


def generate_data_requirements(
    project,
    hypotheses,
    experiments,
    prototype_spec,
):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Approved Hypotheses

{json.dumps(hypotheses, indent=2)}

Approved Experiments

{json.dumps(experiments, indent=2)}

Prototype Specification

{json.dumps(prototype_spec, indent=2)}

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