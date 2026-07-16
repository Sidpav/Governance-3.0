# llm/gain_pain_logic.py
# ─────────────────────────────────────────────────────────────────────────
# Gain-Pain AI logic — preserved verbatim from My Project's
# modules/module3/gainpain.py (_call_m3_ai) and
# modules/module4/dashboard.py (_call_smart_questions_ai).
#
# Pulled out into its own importable module (instead of living inside a
# Streamlit page file) because both pages/3_Gain_Pain_Analysis.py and
# pages/5_Analytics_Dashboard.py need it, and importing a sibling page file
# directly would re-execute that page's entire top-level UI. No prompt
# text, scoring formula, or behaviour was changed in this move.
# ─────────────────────────────────────────────────────────────────────────

import json
import streamlit as st

from config.prompts import M3_GAINPAIN_PROMPT
from utils.helpers import call_ai, clean_llm_json

TEAM_COLORS = {
    "Technical Team":     "#6C63FF",
    "Marketing Team":     "#C07A10",
    "Finance Team":       "#0F6E56",
    "Legal / Compliance": "#1A5276",
    "HR / Change Mgmt":   "#C0392B",
}


def call_m3_ai(problem: dict, assessment: dict, dept_answers: list | None = None) -> dict | None:
    prompt = f"""{M3_GAINPAIN_PROMPT}

PROBLEM STATEMENT (Module 1):
- Problem: {problem.get('problem_statement','')}
- Objective: {problem.get('business_objective','')}
- Solution: {problem.get('solution_approach','')}
- Business value: {problem.get('business_value','')}
- Workflow: {problem.get('workflow_location','')}
- Timeline: {problem.get('timeline','')}
- Owner: {problem.get('action_owner','')}
- ISO Risk Category: {problem.get('iso_risk_category','Not specified')}
- Affected stakeholders: {problem.get('affected_stakeholders','')}
- Success criteria: {problem.get('success_criteria','')}

FEASIBILITY ASSESSMENT (Module 2):
- Overall score: {float(assessment.get('overall_score') or 0):.2f}/5
- Verdict: {assessment.get('verdict','—')}
- AI Suitability: {float(assessment.get('ai_suitability_score') or 0):.1f}
- Economic Viability: {float(assessment.get('economic_viability_score') or 0):.1f}
- Data Readiness: {float(assessment.get('data_readiness_score') or 0):.1f}
- Workflow Maturity: {float(assessment.get('workflow_maturity_score') or 0):.1f}
- Change Management: {float(assessment.get('change_management_score') or 0):.1f}
- Risk & Compliance: {float(assessment.get('risk_compliance_score') or 0):.1f}
- Hard gate triggered: {bool(assessment.get('hard_gate_triggered',0))}

Apply the NIST priority score formula and return ONLY the JSON object."""

    if dept_answers:
        prompt += "\n\nTEAM RESPONSES (evidence provided by teams):\n"
        for i, qa in enumerate(dept_answers, 1):
            q = qa.get('q', '')
            a = qa.get('a', '')
            prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"

    try:
        raw = call_ai(prompt)
        text = clean_llm_json(raw)
        from governance.rules import validate_gain_pain_result
        return validate_gain_pain_result(json.loads(text))
    except json.JSONDecodeError as e:
        st.error(f"AI returned malformed JSON: {e}")
        st.code(raw[:600], language="json")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None


def call_smart_questions_ai(r, gp, asmt, ai_data, selected_teams, q_depth) -> dict | None:
    depth_instruction = ("5-6 specific, evidence-seeking questions" if "Deep" in q_depth
                          else "3-4 specific, evidence-seeking questions")

    gains = ai_data.get("gains", {})
    pains = ai_data.get("pains", {})
    g_r = ai_data.get("gain_reasoning", {})
    p_r = ai_data.get("pain_reasoning", {})

    prompt = f"""You are a senior AI Governance Analyst helping a Central Committee strengthen a Gain-Pain analysis.

PROBLEM:
- Statement: {r.get('problem_statement','')}
- Objective: {r.get('business_objective','')}
- Solution: {r.get('solution_approach','')}
- Business Value: {r.get('business_value','')}
- ISO Risk Category: {r.get('iso_risk_category','')}
- Affected Stakeholders: {r.get('affected_stakeholders','')}
- Data Sources: {r.get('data_sources','')}
- Success Criteria: {r.get('success_criteria','')}

CURRENT GAIN-PAIN SCORES (1-5 scale):
Gains:
  Business Value: {gains.get('business_value_gain',0):.1f} — {g_r.get('business_value_gain','')}
  Strategic Alignment: {gains.get('strategic_alignment',0):.1f} — {g_r.get('strategic_alignment','')}
  Efficiency Gain: {gains.get('efficiency_gain',0):.1f} — {g_r.get('efficiency_gain','')}
  Innovation Potential: {gains.get('innovation_potential',0):.1f} — {g_r.get('innovation_potential','')}
Pains:
  Implementation Cost: {pains.get('implementation_cost',0):.1f} — {p_r.get('implementation_cost','')}
  Operational Risk: {pains.get('operational_risk',0):.1f} — {p_r.get('operational_risk','')}
  Adoption Resistance: {pains.get('adoption_resistance',0):.1f} — {p_r.get('adoption_resistance','')}
  Compliance Burden: {pains.get('compliance_burden',0):.1f} — {p_r.get('compliance_burden','')}

Priority Score: {gp.get('priority_score_scaled',0):.1f}/10 — {gp.get('priority_band','')}

M2 FEASIBILITY:
  Overall: {float(asmt.get('overall_score',0) or 0):.2f}/5
  Verdict: {asmt.get('verdict','')}
  Risk & Compliance: {float(asmt.get('risk_compliance_score',0) or 0):.1f}/5
  Data Readiness: {float(asmt.get('data_readiness_score',0) or 0):.1f}/5

TEAMS TO QUESTION: {', '.join(selected_teams)}
QUESTION DEPTH: {depth_instruction}

Your job:
1. Identify which Gain-Pain dimensions have low confidence, thin evidence, or scores that seem too high/low given the context.
2. For EACH requested team, generate {depth_instruction} that would yield concrete evidence to validate or adjust the current scores.
3. Questions must be specific to THIS use case — not generic. Reference actual numbers, processes, or risks from the problem data.
4. Each question must clearly state which Gain-Pain dimension it impacts and why the answer matters.

RESPOND ONLY with a valid JSON object (no markdown fences):
{{
  "analysis_gaps_summary": "2-3 sentence summary of which dimensions have the most uncertainty and why.",
  "teams": {{
    "<team name exactly as provided>": {{
      "rationale": "One sentence on why this team's input is critical for this specific use case.",
      "questions": [
        {{
          "question": "Specific question text",
          "dimension": "Which gain/pain dimension this clarifies",
          "why": "One sentence on how the answer would change the score"
        }}
      ]
    }}
  }}
}}"""

    try:
        raw = call_ai(prompt)
        text = clean_llm_json(raw)
        return json.loads(text)
    except Exception as e:
        st.error(f"Smart question generation failed: {e}")
        return None
