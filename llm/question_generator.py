# ==========================
# QUESTION MAPPING
# ==========================

QUESTION_MAP = {
    "problem_statement":
        "What is the problem statement (More clear)?",

    "business_objective":
        "What business objective are you trying to achieve?",

    "proposed_solution":
        "What solution approach do you propose?",

    "timeline":
        "What is the expected timeline?",

    "owner":
        "Who owns this process?",

    "workflow_location":
        "Where in the workflow does this problem occur?",

    "decision_support":
        "What decision support is required?",

    "business_value":
        "What is the expected business value or revenue impact?"
}


# ==========================
# QUESTION GENERATION
# ==========================

def generate_questions(
    missing_fields
):

    questions = []

    for field in missing_fields:

        if field in QUESTION_MAP:

            questions.append(
                QUESTION_MAP[field]
            )

    return questions