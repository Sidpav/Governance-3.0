# config/constants.py

# ── Module 1 — Problem Definition (13 fields: 8 original + 5 ISO 42001) ───────
REQUIRED_FIELDS = [
    # Original 8
    ("problem_statement",  "Business problem statement"),
    ("business_objective", "Business objective"),
    ("solution_approach",  "Proposed solution approach"),
    ("workflow_location",  "Workflow / process location"),
    ("decision_support",   "Decision support required"),
    ("business_value",     "Quantified business value"),
    # ISO 42001 additions
    ("iso_risk_category",     "ISO Risk Category"),           # ISO Clause 6.1.2
    ("affected_stakeholders", "Affected stakeholders"),       # ISO Clause 6.1.4
    ("human_override",        "Human oversight & override"),  # ISO Clause 8.4.3
    ("data_sources",          "Data sources & personal data"),# ISO Annex A.8
    ("success_criteria",      "AI success criteria & KPIs"),  # ISO Clause 6.2
]
FIELD_KEYS   = [f[0] for f in REQUIRED_FIELDS]
FIELD_LABELS = {f[0]: f[1] for f in REQUIRED_FIELDS}

ISO_RISK_LEVELS = ["Minimal", "Limited", "High", "Unacceptable"]

# ── Status ─────────────────────────────────────────────────────────────────────
STATUS_OPTIONS = ["Submitted", "Under Review", "Approved", "Rejected", "Deferred"]
STATUS_BADGE   = {
    "Submitted":    "b-submitted",
    "Under Review": "b-review",
    "Approved":     "b-approved",
    "Rejected":     "b-rejected",
    "Deferred":     "b-deferred",
}

# ── Module 2 — Feasibility Assessment (6 dimensions, 37 questions) ─────────────
# Updated per NIST AI RMF: 2 new Qs in AI Suitability, 3 new in Data Readiness,
# 1 new in Workflow Maturity, 1 entirely new Risk & Compliance dimension
ASSESSMENT_DIMENSIONS = [
    {
        "id":    "ai_suitability",
        "label": "AI Suitability",
        "icon":  "🤖",
        "role":  "Process Owner",
        "color": "#6C63FF",
        "desc":  "Evaluates whether the problem is genuinely suitable for AI. Includes NIST MAP assessment of autonomy level and failure severity.",
        "questions": [
            ("pattern_complexity",       "The problem involves complex patterns that are difficult to express as simple rules"),
            ("data_driven",              "The problem is data-driven with variability that rules cannot fully capture"),
            ("ai_over_rules",            "AI would provide measurable advantages over rule-based or traditional ML approaches"),
            ("repeatability",            "The problem occurs frequently enough to justify AI development and maintenance cost"),
            ("outcome_clarity",          "The desired AI output is clearly definable and measurable"),
            # NIST MAP 1.5
            ("autonomous_decision_level","The AI system acts as an advisor only — a human makes every final decision (1=fully autonomous, 5=advisory only)"),
            # NIST MAP 2.3
            ("failure_impact_severity",  "If the AI produces a wrong output, the impact on people and processes is low and easily corrected (1=catastrophic, 5=negligible)"),
        ],
    },
    {
        "id":    "economic_viability",
        "label": "Economic Viability",
        "icon":  "💰",
        "role":  "Finance / Business Lead",
        "color": "#0F6E56",
        "desc":  "Assesses ROI potential, cost of implementation, and scale benefits. Unchanged — existing questions satisfy framework requirements.",
        "questions": [
            ("roi_potential",       "The projected ROI or cost savings justifies the investment in AI development"),
            ("scale_benefit",       "The solution will deliver increasing returns as it scales across the organisation"),
            ("budget_availability", "Adequate budget is available or can be allocated for this initiative"),
            ("time_to_value",       "The time to realise business value is acceptable given the investment required"),
            ("competitive_edge",    "Implementing this AI solution provides a meaningful competitive or operational advantage"),
        ],
    },
    {
        "id":    "data_readiness",
        "label": "Data & Technology Readiness",
        "icon":  "🗄️",
        "role":  "Data / Technology Team",
        "color": "#C07A10",
        "desc":  "Checks data availability, quality, and infrastructure. Expanded with NIST MEASURE requirements for bias, explainability, and monitoring.",
        "questions": [
            ("data_availability",  "Sufficient historical data exists or can be collected to train and validate the AI model"),
            ("data_quality",       "The available data is accurate, complete, and consistent"),
            ("infrastructure",     "The technology infrastructure required to deploy and run this AI solution is in place"),
            ("integration_ease",   "The AI solution can be integrated into existing systems without major re-engineering"),
            ("data_governance",    "Data privacy, security, and governance requirements can be met for this use case"),
            # NIST MEASURE 2.5
            ("explainability",     "The AI system can explain its decisions in plain language to the person affected by them (1=black box, 5=full plain-language explanations)"),
            # NIST MEASURE 2.7
            ("monitoring_plan",    "A defined post-deployment monitoring plan exists, including drift detection and alert owners (1=no plan, 5=automated monitoring with thresholds)"),
        ],
    },
    {
        "id":    "workflow_maturity",
        "label": "Workflow Maturity",
        "icon":  "⚙️",
        "role":  "Operations / Process Owner",
        "color": "#7B32AD",
        "desc":  "Evaluates how well-defined the process is for AI augmentation. Expanded with NIST GOVERN requirement for human-in-the-loop integration.",
        "questions": [
            ("process_defined",    "The current process/workflow is well-documented and clearly defined"),
            ("process_stable",     "The process is stable and not undergoing major changes that would affect AI training"),
            ("exception_handling", "Edge cases and exceptions in the process are understood and manageable"),
            ("kpi_defined",        "Clear KPIs exist to measure success and monitor AI performance post-deployment"),
            ("ownership_clear",    "Process ownership and accountability for the AI-augmented workflow is clearly assigned"),
            # NIST GOVERN 1.2
            ("human_in_loop",     "There is a defined, documented human review step before any AI output results in a consequential action (1=no checkpoint, 5=human reviews every decision)"),
        ],
    },
    {
        "id":    "change_management",
        "label": "Change Management",
        "icon":  "👥",
        "role":  "HR / Change Management",
        "color": "#C0392B",
        "desc":  "Assesses organisational readiness and adoption risk. Unchanged — existing questions satisfy ISO 7.2, 7.3, 7.4 requirements.",
        "questions": [
            ("leadership_support",   "Senior leadership actively supports and champions this AI initiative"),
            ("user_acceptance",      "End users are likely to accept and trust AI-assisted decision-making in this area"),
            ("training_feasibility", "Training and upskilling programs for impacted staff are feasible within the timeline"),
            ("resistance_risk",      "The risk of significant employee resistance or pushback is low and manageable"),
            ("culture_readiness",    "The organisational culture is ready to embrace AI-augmented processes"),
        ],
    },
    {
        "id":    "risk_compliance",
        "label": "Risk & Compliance",
        "icon":  "⚖️",
        "role":  "Legal / Compliance / Risk Team",
        "color": "#1A5276",
        "desc":  "NEW dimension per NIST GOVERN + ISO 42001 Clause 6.1.3. Assesses regulatory compliance, ethical risk, audit trail feasibility, and legal liability.",
        "questions": [
            # NIST GOVERN 6.1
            ("ethical_risk",            "The AI system does not create unacceptable ethical risks such as discrimination, manipulation, or violation of individual rights"),
            # NIST MAP 5.1
            ("audit_trail_feasibility", "It is technically feasible to create and maintain a complete audit trail of all AI decisions for the required retention period"),
            ("third_party_risk",        "Any third-party AI tools, models, or data providers involved meet the organisation's risk and compliance standards"),
            ("legal_liability_clarity", "Legal liability for incorrect or harmful AI outputs is clearly defined and covered by existing policy or insurance"),
        ],
    },
]

VERDICT_CONFIG = {
    "Feasible":     {"color": "#1D9E75", "bg": "#D1F5EA", "icon": "✅"},
    "Conditional":  {"color": "#C07A10", "bg": "#FFF3CD", "icon": "⚠️"},
    "Not Feasible": {"color": "#C0392B", "bg": "#FDE8E8", "icon": "❌"},
}

# ── Module nav ─────────────────────────────────────────────────────────────────
MODULES = [
    ("m1", "01", "Problem Definition",    "Active"),
    ("m2", "02", "Feasibility Assessment", "Active"),
    ("m3", "03", "Gain–Pain Analysis",     "Locked"),
    ("m4", "04", "Committee Decision",     "Locked"),
    ("m5", "05", "Governance Dashboard",   "Locked"),
]


# ── Module 3 — Gain Pain Analysis ─────────────────────────────────────────────
GAIN_DIMENSIONS = [
    {"id": "business_value_gain",  "label": "Business Value Gain",  "icon": "💰", "nist": "MAP 1.4"},
    {"id": "strategic_alignment",  "label": "Strategic Alignment",  "icon": "🎯", "nist": "MAP 1.3"},
    {"id": "efficiency_gain",      "label": "Efficiency Gain",      "icon": "⚡", "nist": "MAP 3.1"},
    {"id": "innovation_potential", "label": "Innovation Potential", "icon": "🚀", "nist": "MAP 3.3"},
]

PAIN_DIMENSIONS = [
    {"id": "implementation_cost",  "label": "Implementation Cost",  "icon": "💸", "nist": "MAP 3.2"},
    {"id": "operational_risk",     "label": "Operational Risk",     "icon": "⚠️", "nist": "MAP 2.3"},
    {"id": "adoption_resistance",  "label": "Adoption Resistance",  "icon": "🔄", "nist": "GOVERN 4.2"},
    {"id": "compliance_burden",    "label": "Compliance Burden",    "icon": "⚖️", "nist": "MAP 1.1"},
]

PRIORITY_BANDS = {
    "High Priority":   {"color": "#1D9E75", "bg": "#D1F5EA", "icon": "🟢"},
    "Medium Priority": {"color": "#C07A10", "bg": "#FFF3CD", "icon": "🟡"},
    "Low Priority":    {"color": "#C0392B", "bg": "#FDE8E8", "icon": "🔴"},
}

# ── Scoring basis: shown below each M2 dimension bar ─────────────────────────
# Tells the user WHAT the AI evaluated when producing that score.
M2_SCORING_BASIS = {
    "ai_suitability": (
        "Scored on: pattern complexity, data-driven variability, AI advantage over rules, "
        "repeatability of the problem, clarity of the desired output, autonomy level "
        "(advisory vs. fully autonomous), and severity of wrong AI output on people and processes."
    ),
    "economic_viability": (
        "Scored on: projected ROI / cost savings, scale benefit as the solution grows, "
        "budget availability, acceptable time-to-value, and competitive or operational advantage gained."
    ),
    "data_readiness": (
        "Scored on: availability and quality of historical data, technology infrastructure, "
        "ease of integration into existing systems, data governance and PII compliance, "
        "bias audit status of training data, explainability of AI decisions, "
        "and existence of a post-deployment drift-monitoring plan."
    ),
    "workflow_maturity": (
        "Scored on: how well-documented and stable the current process is, "
        "how well edge cases are understood, existence of clear KPIs, "
        "clarity of ownership, and presence of a defined human review checkpoint "
        "before any consequential AI decision is acted on."
    ),
    "change_management": (
        "Scored on: leadership support and sponsorship, user acceptance and willingness to adopt, "
        "training feasibility for staff affected by the change, "
        "and ability to manage cultural or procedural resistance."
    ),
    "risk_compliance": (
        "Scored on: regulatory and legal compliance readiness, ethical risk "
        "(discrimination, manipulation, privacy), existence of an audit trail, "
        "third-party AI component risk, and legal liability exposure."
    ),
}

# ── Scoring basis: shown below each M3 gain / pain bar ───────────────────────
M3_SCORING_BASIS = {
    # Gains
    "business_value_gain": (
        "Scored on: quantified financial and operational benefit — revenue increase, "
        "cost savings, or hours saved. Requires a concrete number to score above 3.0."
    ),
    "strategic_alignment": (
        "Scored on: how well this use case aligns with the organisation's stated AI strategy, "
        "digital transformation roadmap, and top-level business objectives."
    ),
    "efficiency_gain": (
        "Scored on: measurable improvements in process speed, accuracy, error reduction, "
        "and unit cost of the affected workflow after AI deployment."
    ),
    "innovation_potential": (
        "Scored on: long-term competitive advantage, potential to open new markets or "
        "capabilities, and the degree to which this use case advances the organisation's "
        "AI maturity."
    ),
    # Pains
    "implementation_cost": (
        "Scored on: total estimated cost of development, data preparation, infrastructure, "
        "integration, testing, and ongoing maintenance. Higher score = more painful / costly."
    ),
    "operational_risk": (
        "Scored on: risk of AI failure, wrong outputs, or unintended consequences in "
        "production, and severity of impact on people and processes. Higher score = higher risk."
    ),
    "adoption_resistance": (
        "Scored on: expected resistance from end-users, middle management, or regulators; "
        "change-fatigue risk; and cultural or process friction. Higher score = harder adoption."
    ),
    "compliance_burden": (
        "Scored on: regulatory overhead, audit requirements, legal review cycles, GDPR / "
        "data-protection obligations, and ISO or NIST compliance documentation needed. "
        "Higher score = heavier compliance burden."
    ),
}

# ── Formula tooltips: HTML for the ℹ icon popovers ────────────────────────────
INFO_ICON_HTML = (
    '<span class="info-wrap" tabindex="0">'
    '<span class="info-icon">i</span>'
    '<span class="info-tooltip">{content}</span>'
    '</span>'
)

M2_OVERALL_FORMULA_HTML = INFO_ICON_HTML.format(content=(
    "<b>Overall Governance Score</b><br>"
    "1. Calculate the average of the six assessment dimensions.<br>"
    "2. Apply the ISO 42001 risk adjustment (if applicable).<br>"
    "3. Check for governance Hard Gates.<br>"
    "4. Determine the final verdict.<br><br>"

    "<b>Hard Gate Rules</b><br>"
    "• Critical legal, regulatory, ethical or governance risks trigger a Hard Gate.<br>"
    "• A Hard Gate overrides the numerical score.<br>"
    "• The reason is recorded as <code>hard_gate_reason</code>.<br><br>"

    "<b>ISO Risk Adjustment</b><br>"
    "• High Risk → deduct 0.3 from the average score before assigning the verdict.<br><br>"

    "<b>Verdict Thresholds</b><br>"
    "• ≥ 3.5 → ✅ Feasible<br>"
    "• 2.5–3.49 → ⚠️ Conditional<br>"
    "• &lt;2.5 → ❌ Not Feasible"
))

M3_PRIORITY_FORMULA_HTML = INFO_ICON_HTML.format(content=(
    "<b>Governance Priority Score</b><br>"
    "<code>avg_gains = mean(4 gain scores)</code><br>"
    "<code>avg_pains = mean(4 pain scores)</code><br>"
    "<code>raw = (avg_gains × 0.6) − (avg_pains × 0.4)</code><br>"
    "<code>scaled = ((raw + 2) / 5) × 10</code><br><br>"

    "<b>Evidence Rules</b><br>"
    "• Only evidence explicitly provided is rewarded.<br>"
    "• Unknown implementation effort increases Pain.<br>"
    "• Unknown compliance effort increases Pain.<br>"
    "• Unquantified business value limits Gain.<br><br>"

    "<b>Priority Bands</b><br>"
    "• ≥7.0 → 🟢 High Priority<br>"
    "• 4.0–6.9 → 🟡 Medium Priority<br>"
    "• &lt;4.0 → 🔴 Low Priority"
))

M3_AVG_GAINS_FORMULA_HTML = INFO_ICON_HTML.format(content=(
    "<b>Avg Gains</b><br>"
    "<code>avg_gains = (Business Value + Strategic Alignment "
    "+ Efficiency Gain + Innovation Potential) / 4</code><br><br>"
    "Each dimension scored 1.0–5.0 by the AI."
))

M3_AVG_PAINS_FORMULA_HTML = INFO_ICON_HTML.format(content=(
    "<b>Avg Pains</b><br>"
    "<code>avg_pains = (Implementation Cost + Operational Risk "
    "+ Adoption Resistance + Compliance Burden) / 4</code><br><br>"
    "Each dimension scored 1.0–5.0. Higher = more painful / risky."
))

# Unlock Module 3, Committee, and Dashboard
MODULES = [
    ("m1", "01", "Problem Definition",    "Active"),
    ("m2", "02", "Feasibility Assessment", "Active"),
    ("m3", "03", "Gain–Pain Analysis",     "Active"),
    ("m4", "04", "Committee Decision",     "Active"),
    ("m5", "05", "Governance Dashboard",   "Active"),
]

NIST_REFERENCES = {

    "MAP 1.4": {
        "title": "Business Value",
        "description":
            "The business value or context of business use has been clearly defined or re-evaluated."
    },

    "MAP 1.3": {
        "title": "Strategic Alignment",
        "description":
            "The organization's mission and relevant goals for AI technology are understood and documented."
    },

    "MAP 3.1": {
        "title": "Expected Benefits",
        "description":
            "Potential benefits of intended AI system functionality and performance are examined and documented."
    },

    "MAP 3.3": {
        "title": "Application Scope",
        "description":
            "Targeted application scope is specified and documented based on the system capability and context."
    },

    "MAP 3.2": {
        "title": "Costs",
        "description":
            "Potential costs, including non-monetary costs resulting from AI functionality, are examined and documented."
    },

    "MAP 2.3": {
        "title": "Operational Risk",
        "description":
            "Scientific integrity, data quality, validation, and trustworthiness considerations are identified and documented."
    },

    "GOVERN 4.2": {
        "title": "Stakeholder Communication",
        "description":
            "Organizational teams document AI risks and communicate potential impacts to relevant stakeholders."
    },

    "MAP 1.1": {
        "title": "Compliance Context",
        "description":
            "The intended purpose, applicable laws, regulations, norms, expectations, and deployment context are understood and documented."
    }

}
