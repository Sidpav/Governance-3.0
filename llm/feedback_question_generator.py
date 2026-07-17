import json
import re

from llm.ai_provider import generate_response


ROLES = [
    "Product Lead",
    "Business Head",
    "Data Lead",
    "Compliance Lead",
    "Infrastructure Lead",
]


SYSTEM_PROMPT = """
You are a Senior AI Governance Review Board.

Generate a project-specific stakeholder review questionnaire for an AI
prototype using the supplied business problem, hypotheses, experiments, and
prototype specification.

Stakeholders:
1. Product Lead
2. Business Head
3. Data Lead
4. Compliance Lead
5. Infrastructure Lead

Rules:
- Every stakeholder must receive 12 to 18 questions.
- Divide each questionnaire into 4 to 6 logical sections.
- Every section must contain 3 to 5 questions.
- Questions must be specific to this project and support a pilot decision.
- Include expected evidence, help text, and High/Medium/Low importance.
- Cover transparency, privacy, fairness, human oversight, accountability,
  evidence completeness, model use, operational controls, and monitoring.
- Return JSON only. Do not use Markdown fences or commentary.

Required JSON shape:
{
  "stakeholders": [
    {
      "role": "Product Lead",
      "objective": "",
      "sections": [
        {
          "title": "",
          "questions": [
            {
              "question": "",
              "importance": "High",
              "expected_evidence": "",
              "help_text": ""
            }
          ]
        }
      ]
    }
  ]
}
"""


ROLE_SECTIONS = {
    "Product Lead": [
        ("Learner Outcomes", [
            "Are the intended learner outcomes and target learner groups clearly defined?",
            "Is there evidence that the proposed recommendations address a validated learner need?",
            "Are success measures defined for recommendation usefulness, learner confidence, and certification readiness?",
        ]),
        ("Recommendation Experience", [
            "Can learners understand why a pathway, resource, or preparation activity was recommended?",
            "Can learners reject, question, or request human review of a recommendation?",
            "Are accessibility, language, geography, and experience-level needs included in the experience design?",
        ]),
        ("Pilot Controls", [
            "Is the pilot scope limited to defined learner groups, courses, and recommendation types?",
            "Are product owners identified for content quality, learner communications, and issue resolution?",
            "Are exit criteria defined for pausing or changing the pilot when outcomes are poor?",
        ]),
        ("Monitoring", [
            "Will recommendation acceptance, completion, appeals, and negative feedback be monitored?",
            "Is there a process for updating learning resources when certifications or course content change?",
            "Will product decisions and human overrides be retained for later review?",
        ]),
    ],
    "Business Head": [
        ("Strategic Alignment", [
            "Is the initiative aligned with professional learning, member value, and responsible technology objectives?",
            "Is the business problem sufficiently important to justify an AI-enabled intervention?",
            "Are expected benefits separated from assumptions that still require pilot validation?",
        ]),
        ("Value and Adoption", [
            "Are baseline measures available for participation, completion, certification readiness, and learner confidence?",
            "Are value estimates supported by learner volumes, fee assumptions, and realistic adoption rates?",
            "Does the value case include non-revenue outcomes such as fairness, trust, and learning effectiveness?",
        ]),
        ("Accountability", [
            "Is one accountable business owner named for the pilot and its learner outcomes?",
            "Are decision rights defined across education, privacy, data, technology, and governance teams?",
            "Are approval conditions and unresolved risks assigned to named owners and dates?",
        ]),
        ("Pilot Decision", [
            "Is the evidence complete enough to recommend a controlled pilot rather than further discovery?",
            "Are budget, timeline, staffing, and vendor dependencies documented?",
            "Are measurable go, pause, revise, and stop criteria approved?",
        ]),
    ],
    "Data Lead": [
        ("Data Readiness", [
            "Are learner profiles, course activity, assessment responses, feedback, and content metadata available and documented?",
            "Are data ownership, lineage, quality, completeness, and refresh frequency known for each source?",
            "Is missing or inconsistent data measured across learner groups and regions?",
        ]),
        ("Representativeness and Fairness", [
            "Is the pilot data representative across geography, language, experience level, and accessibility needs?",
            "Are protected or sensitive attributes excluded, controlled, or justified for fairness testing?",
            "Are subgroup performance and recommendation-quality tests defined before pilot launch?",
        ]),
        ("Model Evidence", [
            "Are training, evaluation, and holdout datasets separated and versioned where a predictive model is used?",
            "Are model, rules, retrieval sources, prompts, and content versions documented?",
            "Are accuracy, calibration, error, drift, and low-confidence thresholds defined?",
        ]),
        ("Data Operations", [
            "Are data validation and failure-handling controls implemented before recommendations are generated?",
            "Can data corrections and learner requests propagate to downstream recommendations?",
            "Are monitoring datasets and evidence retention sufficient for ongoing review?",
        ]),
    ],
    "Compliance Lead": [
        ("Privacy and Consent", [
            "Is the purpose for using learner data clearly communicated and appropriately consented?",
            "Are collection, access, retention, deletion, and cross-region transfer requirements documented?",
            "Is sensitive learner information minimized and protected from unnecessary model or vendor exposure?",
        ]),
        ("Transparency and Contestability", [
            "Are learners told that recommendations are AI-assisted and advisory rather than certification decisions?",
            "Are meaningful explanations available for recommendations and their limitations?",
            "Can learners appeal, correct information, or obtain review from a qualified human?",
        ]),
        ("Fairness and Harm", [
            "Are potential harms to confidence, participation, access, and certification preparation documented?",
            "Are fairness tests and acceptance thresholds defined for relevant learner groups?",
            "Is there a process to investigate, remediate, and communicate harmful or biased outcomes?",
        ]),
        ("Governance Evidence", [
            "Are approvals, overrides, incidents, changes, and reviewer comments retained in an auditable record?",
            "Are mandatory privacy, legal, accessibility, and governance reviews completed before real learner data is used?",
            "Are monitoring frequency, escalation paths, and periodic reassessment responsibilities approved?",
        ]),
    ],
    "Infrastructure Lead": [
        ("Architecture and Model Use", [
            "Is it documented whether the solution uses rules, machine learning, an LLM, retrieval, or a combination?",
            "Are model providers, versions, hosting locations, integrations, and data flows documented?",
            "Are external model and API restrictions compatible with learner-data requirements?",
        ]),
        ("Security Controls", [
            "Are authentication, role-based access, encryption, secrets management, and environment separation implemented?",
            "Are learner data and prompts masked or de-identified where required?",
            "Are security testing, vulnerability management, and third-party assurance evidence available?",
        ]),
        ("Reliability and Human Fallback", [
            "Are availability targets, rate limits, recovery procedures, and failure modes defined?",
            "Does the system fail safely when model outputs, source data, or external services are unavailable?",
            "Can a human reviewer intervene without losing the recommendation history or audit evidence?",
        ]),
        ("Operational Monitoring", [
            "Are quality, latency, cost, security, drift, and incident metrics monitored with named owners?",
            "Are prompts, inputs, outputs, versions, overrides, and approvals logged with appropriate privacy controls?",
            "Are rollback, model change, content update, and incident escalation procedures tested?",
        ]),
    ],
}


def _question(text, importance="High"):
    return {
        "question": text,
        "importance": importance,
        "expected_evidence": "Documented policy, owner confirmation, test result, process record, or approved pilot evidence.",
        "help_text": "Answer using evidence available for this project; mark evidence required when the claim is not yet supported.",
    }


def fallback_feedback_questions(project=None):
    project_name = (project or {}).get("problem_statement", "the proposed AI prototype")
    stakeholders = []
    for role in ROLES:
        sections = [
            {"title": title, "questions": [_question(q) for q in questions]}
            for title, questions in ROLE_SECTIONS[role]
        ]
        stakeholders.append({
            "role": role,
            "objective": f"Assess {project_name} from the {role.lower()} perspective before pilot approval.",
            "sections": sections,
        })
    return {"stakeholders": stakeholders, "generation_source": "governance_fallback"}


def _parse_json_response(response):
    if not isinstance(response, str) or not response.strip():
        raise ValueError("The model returned an empty response.")

    cleaned = response.strip().lstrip("\ufeff")
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    candidates = [cleaned]
    first, last = cleaned.find("{"), cleaned.rfind("}")
    if first >= 0 and last > first:
        candidates.append(cleaned[first:last + 1])

    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        for index, char in enumerate(candidate):
            if char != "{":
                continue
            try:
                parsed, _ = decoder.raw_decode(candidate[index:])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
    raise ValueError("The model response did not contain valid questionnaire JSON.")


def _normalise_questionnaire(payload, project):
    fallback = fallback_feedback_questions(project)
    supplied = {
        item.get("role"): item
        for item in payload.get("stakeholders", [])
        if isinstance(item, dict) and item.get("role")
    }

    normalised = []
    for fallback_stakeholder in fallback["stakeholders"]:
        role = fallback_stakeholder["role"]
        stakeholder = supplied.get(role, {})
        valid_sections = []
        for section in stakeholder.get("sections", []):
            if not isinstance(section, dict):
                continue
            valid_questions = []
            for item in section.get("questions", []):
                if not isinstance(item, dict) or not str(item.get("question", "")).strip():
                    continue
                valid_questions.append({
                    "question": str(item["question"]).strip(),
                    "importance": item.get("importance", "High") if item.get("importance") in {"High", "Medium", "Low"} else "High",
                    "expected_evidence": str(item.get("expected_evidence", "Documented project evidence.")),
                    "help_text": str(item.get("help_text", "Answer using available project evidence.")),
                })
            if valid_questions:
                valid_sections.append({
                    "title": str(section.get("title", "Review Questions")),
                    "questions": valid_questions,
                })

        question_count = sum(len(s["questions"]) for s in valid_sections)
        if question_count < 12:
            valid_sections = fallback_stakeholder["sections"]

        normalised.append({
            "role": role,
            "objective": str(stakeholder.get("objective") or fallback_stakeholder["objective"]),
            "sections": valid_sections,
        })

    return {"stakeholders": normalised, "generation_source": "ai"}


def generate_feedback_questions(project, hypotheses, experiments, prototype_spec):
    prompt = f"""
Project
{json.dumps(project, indent=2, default=str)}

Approved Hypotheses
{json.dumps(hypotheses, indent=2, default=str)}

Approved Experiments
{json.dumps(experiments, indent=2, default=str)}

Prototype Specification
{json.dumps(prototype_spec, indent=2, default=str)}
"""

    try:
        response = generate_response(SYSTEM_PROMPT + prompt)
        parsed = _parse_json_response(response)
        return _normalise_questionnaire(parsed, project)
    except Exception:
        return fallback_feedback_questions(project)
