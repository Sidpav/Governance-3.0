# ==========================
# IMPORTING LIBRARIES
# ==========================

from llm.ai_provider import generate_response
import json

# ==========================
# PROBLEM EXTRACTION
# ==========================

def extract_problem(
    problem_text,
    provider
):

    prompt = f"""
    Extract information from the business problem below.

   Use information explicitly stated whenever possible.

    For missing information,
    make reasonable business inferences.

    Never return null.

    Never return None.

    If information cannot be confidently inferred,
    return an empty string "".

    All fields must be present in the JSON.
    Return ONLY valid JSON.

    Additionally identify
    Stakeholders:
    Identify employees, customers, departments,
    or external parties likely to be affected.

    Why AI:
    Explain why AI provides value compared with
    manual processes or traditional automation.

    Data Sensitivity:
    Infer the most likely classification:

    Public
    Internal
    Confidential
    Personal Data (PII)

    Examples:

    Resumes -> Personal Data (PII)

    Customer tickets -> Personal Data (PII)

    Financial reports -> Confidential

    Operational metrics -> Internal

    {{
    "problem_statement": "",
    "business_objective": "",
    "proposed_solution": "",
    "timeline": "",
    "owner": "",
    "workflow_location": "",
    "decision_support": "",
    "business_value": "",

    "stakeholders": "",
    "why_ai": "",
    "data_sensitivity": ""
}}
        IMPORTANT:

        Return ONLY valid JSON.

        Do not include explanations.

        Do not include markdown.

        Do not include ```json.

        Do not include text before or after the JSON.

        Your response must start with {{ and end with }}.
    Business Problem:

    {problem_text}
    """

    # ==========================
    # LLM CALL
    # ==========================

    content = generate_response(
        prompt=prompt,
        provider=provider
    )

    # ==========================
    # RESPONSE CLEANING
    # ==========================

    print("\nRAW RESPONSE:")
    print(content)

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()

    # ==========================
    # VALIDATION
    # ==========================

    if not content:

        raise ValueError(
            "Model returned empty response."
        )

    # ==========================
    # JSON PARSING
    # ==========================

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        print("\nFAILED JSON:")
        print(content)

        raise ValueError(
            "Model did not return valid JSON."
        )