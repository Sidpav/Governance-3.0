import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT="""
You are a Senior AI Governance Review Board.

Your task is to generate a comprehensive stakeholder review questionnaire for an AI prototype.

Context available:
- Business Problem
- Business Objectives
- Approved Hypotheses
- Approved Experiments
- Prototype Specification

Generate questionnaires for ALL stakeholders.

Stakeholders:
1. Product Lead
2. Business Head
3. Data Lead
4. Compliance Lead
5. Infrastructure Lead

Rules:

- Every stakeholder MUST receive 12–18 questions.
- Divide questions into 4–6 logical sections.
- Every section must contain 3–5 questions.
- Questions must be specific to THIS project.
- Do NOT ask generic AI questions.
- Questions should help determine whether the prototype is ready to proceed.
- Include expected evidence for every question.
- Include importance (High/Medium/Low).

Do not generate fewer than 12 questions for any stakeholder.

If fewer than 12 questions are generated for any stakeholder, regenerate until the requirement is met.

Return ONLY valid JSON.

{
    "stakeholders":[

        {
            "role":"Product Lead",

            "objective":"",

            "sections":[

                {
                    "title":"",

                    "questions":[

                        {
                            "question":"",

                            "importance":"High",

                            "expected_evidence":"",

                            "help_text":""
                        }

                    ]

                }

            ]

        }

    ]
}

}
"""


def generate_feedback_questions(
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

        if start == -1 or end == 0:
            raise ValueError(
                f"LLM did not return JSON.\n\nResponse:\n{response}"
            )

        return json.loads(response[start:end])