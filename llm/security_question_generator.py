import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an AI Infrastructure and Security Architect.

Using the provided project information, generate security review questions
specific to this AI project.

Consider:

- Data sensitivity
- Deployment model
- Infrastructure decisions
- AI model choice
- APIs
- Authentication
- Authorization
- Encryption
- Audit logging
- Model security
- Infrastructure security
- Regulatory concerns

Return ONLY valid JSON.

{
    "security_questions":[
        {
            "category":"",
            "question":""
        }
    ]
}

Requirements:

- Generate 8-12 questions.
- Questions must be specific to this project.
- Include multiple categories.
- Return JSON only.
"""

def generate_security_questions(

    project,

    prototype_spec,

    infrastructure_decisions,

    infrastructure_recommendation,

):

    prompt = f"""

Project

{json.dumps(project, indent=2)}

Prototype Specification

{json.dumps(prototype_spec, indent=2)}

Infrastructure Decisions

{json.dumps(infrastructure_decisions, indent=2)}

Infrastructure Recommendation

{json.dumps(infrastructure_recommendation, indent=2)}

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

        return json.loads(response[start:end])