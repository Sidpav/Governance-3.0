import json

from llm.ai_provider import generate_response


SYSTEM_PROMPT = """
You are an AI Governance implementation consultant.

Your task is to generate implementation hypotheses for an approved AI project.

Generate between 3 and 5 hypotheses.

Each hypothesis must contain:

Requirements:

- measurable
- testable
- implementation focused
- business oriented

Return ONLY valid JSON.

Example:

[
    {
    "title": "",
    "category": "",
    "priority": "",
    "status": "Proposed",

    "description": "",
    "reasoning": "",
    "what_this_tests": "",
    "risk_if_wrong": "",

    "evidence_problem": "",
    "evidence_documents": "",
    "contradictions": "",
    "business_dependency": "",
    "feasibility_dependency": "",
    "risk_if_not_tested": "",

    "success_metric": "",

    "expert_review": {
        "agreement": "",
        "edited_title": "",
        "edited_description": "",
        "edited_reasoning": "",
        "edited_metric": "",
        "additional_assumption": "",
        "critical": false,
        "comments": ""
    }
]
"""


def generate_hypotheses(project):

    prompt = f"""
Problem Statement:
{project.get("problem_statement")}

Business Objective:
{project.get("business_objective")}

Solution:
{project.get("solution_approach")}

Business Value:
{project.get("business_value")}

Workflow Location:
{project.get("workflow_location")}
"""

    full_prompt = f"""
    {SYSTEM_PROMPT}

    {prompt}
    """

    response = generate_response(full_prompt)

    try:

        return json.loads(response)

    except Exception:

        try:

            start = response.index("[")

            end = response.rindex("]") + 1

            return json.loads(response[start:end])

        except Exception:

            return []