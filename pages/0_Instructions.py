# pages/0_Instructions.py
#
# Getting-Started / User Guide page. Sits before "Problem Definition" in the
# sidebar's "Getting Started" section. Uses the platform's real unified
# theme (ui/theme.py) and sidebar (ui/sidebar.py) — no separate CSS, no
# separate logo-watermark code — so this page is visually identical to
# every other page rather than a bolted-on standalone style.
#
# Content describes the ACTUAL modules in this app (13-field ISO-aligned
# intake, 6-dimension NIST/ISO feasibility assessment with hard gates,
# 8-dimension Gain-Pain analysis, Committee Decision, Governance Dashboard,
# and Expert Advice) rather than a generic placeholder workflow.

import streamlit as st

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar
from ui.auth import require_login, require_access

# ==========================
# PAGE CONFIGURATION
# ==========================

st.set_page_config(
    page_title="AI Governance Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_login()

apply_theme()
render_sidebar("instructions")
render_navbar("instructions")
require_access("instructions")

# ==========================
# TITLE
# ==========================

st.title("📘 AI Governance Platform — User Guide")

st.info(
    "This platform helps organizations identify, evaluate, prioritize, and "
    "govern AI opportunities through a structured workflow aligned with "
    "**ISO/IEC 42001** and the **NIST AI Risk Management Framework**."
)

# ==========================
# OVERVIEW
# ==========================

st.subheader("Platform Workflow")

st.markdown("""
1. **Use-case Intake** — describe an idea or upload documents; AI extracts, proposes, and checks consistency
2. **Use-case Scoring & Prioritization** — AI scores readiness across 6 dimensions
3. **Value-Risk Assessment** — AI scores benefit vs. risk across 8 dimensions
4. **Portfolio Gate Review** — governance board records Approve / Reject / Conditional / Defer
5. **Portfolio Dashboard** — portfolio-level visibility across all opportunities
6. **Expert Advice** — raise concerns or have an expert review and adjust scoring
""")

st.divider()

# ==========================
# MODULE 1 — IDEA SUBMISSION
# ==========================

st.subheader("💡 Use-case Intake")

st.markdown("""
Describe a business idea, problem statement, or use case in free text — and/or
upload supporting documents (PDF, DOCX, PPTX, XLSX, CSV, TXT). The platform
walks through six steps:

1. **Describe** — type a description and/or attach files (multiple supported).
2. **Auto-Capture** — AI reads everything together and proposes a **Problem
   Statement** and **Business Objective**, which you can edit.
3. **Key Details** — you're asked directly for **Business Value**, **Workflow
   Location**, and **Decision Support**. The AI never invents these — vague
   answers (e.g. "TBD") won't be accepted for business value.
4. **Proposed Solution** — AI proposes a concrete solution type (e.g. Copilot,
   Predictive Analytics Platform, Agentic AI System) with expected benefits.
   If it's not right, answer a few targeted clarification questions and the
   AI will refine it — this can repeat until you're satisfied.
5. **Consistency Check** — if you uploaded documents, the platform compares
   what you typed against what the documents say, flagging any material
   contradictions with the exact file, page/slide/sheet, and confidence level.
6. **Review & Save** — confirm everything (including timeline, owner, and data
   sensitivity) before saving.

⚠️ Any contradictions flagged in Step 5 are saved alongside the submission so
the governance committee can see them during review.
""")

st.divider()

# ==========================
# MODULE 2 — FEASIBILITY ASSESSMENT
# ==========================

st.subheader("📊 Use-case Scoring & Prioritization")

st.markdown("""
An AI Feasibility Analyst scores the submitted problem across **6
dimensions**, each from 1.0 to 5.0, applying the NIST AI RMF and ISO 42001:

| Dimension | What it evaluates |
|---|---|
| 🤖 AI Suitability | Pattern complexity, autonomy level, failure severity |
| 💰 Economic Viability | ROI, scale, budget, time-to-value |
| 🗄️ Data Readiness | Data availability, quality, bias risk, explainability |
| ⚙️ Workflow Maturity | Process stability, KPIs, human-in-the-loop integration |
| 👥 Change Management | Leadership support, user acceptance, training feasibility |
| ⚖️ Risk & Compliance | Regulatory compliance, ethical risk, audit trail, legal liability |

**Hard gate rules** — these override the overall average and force a
verdict regardless of how high other scores are:

* Data Readiness ≤ 2.0 → verdict is forced to **Not Feasible**
* Risk & Compliance ≤ 2.0 → verdict is forced to **Not Feasible**
* ISO Risk Category = **High** → a 0.3 penalty is applied to the overall average

**Verdict thresholds** (after gates and penalties):

* ✅ Average ≥ 3.5 → **Feasible**
* ⚠️ Average 2.5–3.49 → **Conditional**
* ❌ Average < 2.5 → **Not Feasible**

The AI also returns reasoning per dimension, strengths, risks, and
recommendations — review these rather than just the number.
""")

st.divider()

# ==========================
# MODULE 3 — GAIN-PAIN ANALYSIS
# ==========================

st.subheader("⚖️ Value-Risk Assessment")

st.markdown("""
Once a problem has been assessed, the AI scores it across **4 Gain
dimensions** and **4 Pain dimensions** (1.0–5.0 each):

**Gains** — 💰 Business Value · 🎯 Strategic Alignment · ⚡ Efficiency Gain · 🚀 Innovation Potential

**Pains** — 💸 Implementation Cost · ⚠️ Operational Risk · 🔄 Adoption Resistance · ⚖️ Compliance Burden

These combine into a single **Priority Score (0–10)**, banded as:

* 🟢 **High Priority** — pursue immediately
* 🟡 **Medium Priority** — schedule with conditions
* 🔴 **Low Priority** — defer or reconsider

The AI also surfaces **quick wins**, **mitigation actions**, and — where
evidence is thin — suggests which team (Technical, Marketing, Finance,
Legal/Compliance, HR) should be consulted before the score is finalized.

⚠️ **A note on trust:** these scores are an AI's qualitative judgment based
on the text you provided, not a deterministic calculation against
objective inputs. Treat the Priority Score as a starting point for
committee discussion, not a final verdict.
""")

st.divider()

# ==========================
# MODULE 4 — COMMITTEE DECISION
# ==========================

st.subheader("🏛️ Portfolio Gate Review")

st.markdown("""
The Governance Board reviews each opportunity's full record — problem
summary, feasibility verdict, and Value-Risk analysis — and records a
formal decision:

* ✅ **Approved**
* ❌ **Rejected**
* ⏳ **Pending Review**
* 🔄 **Needs More Information**

Every decision is timestamped and stored, building an auditable history
for each opportunity.
""")

st.divider()

# ==========================
# MODULE 5 — GOVERNANCE DASHBOARD
# ==========================

st.subheader("📊 Portfolio Dashboard")

st.markdown("""
Portfolio-level visibility across every AI opportunity submitted to the
platform:

* Total opportunities and approval statistics
* Feasibility vs. Value-Risk priority comparison
* Top-priority opportunities at a glance
* Drill-down into any individual opportunity's full history
* ISO 42001 / NIST AI RMF alignment tracking across the portfolio
""")

st.divider()

# ==========================
# MODULE 6 — EXPERT ADVICE
# ==========================

st.subheader("🧑‍⚖️ Expert Advice")

st.markdown("""
If a Value-Risk score looks wrong, anyone can **raise a concern** here
instead of silently distrusting the number. A domain expert can then:

* Review the original AI-generated scores and reasoning
* Adjust individual dimension scores with a documented reason
* Have the override applied and logged to the audit trail

This is the platform's built-in mechanism for catching AI scoring
mistakes — use it whenever a result doesn't match your own judgment.
""")

st.divider()

# ==========================
# FRAMEWORKS
# ==========================

st.subheader("🏛️ Governance Frameworks Used")

c1, c2, c3 = st.columns(3)

with c1:
    st.success("""
    **ISO/IEC 42001**

    Focus:
    * Organisational governance
    * Accountability structures
    * Management-system controls
    """)

with c2:
    st.info("""
    **NIST AI RMF**

    Focus:
    * Risk management (GOVERN / MAP / MEASURE / MANAGE)
    * Fairness & bias
    * Trustworthiness & monitoring
    """)

with c3:
    st.warning("""
    **Combined**

    This platform applies both frameworks together —
    ISO 42001 for governance structure, NIST AI RMF
    for technical risk scoring — for balanced coverage.
    """)

st.divider()

# ==========================
# RECOMMENDED PROCESS
# ==========================

st.subheader("✅ Recommended Workflow")

st.markdown("""
1. Submit a new AI opportunity in **Use-case Intake**.
2. Run the **Use-case Scoring & Prioritization**.
3. Run the **Value-Risk Assessment** — answer any AI-suggested follow-up questions first.
4. Take it to **Portfolio Gate Review** for a formal Approve / Reject outcome.
5. Track the whole portfolio in the **Portfolio Dashboard**.
6. If a score looks off at any stage, use **Expert Advice** to flag or correct it.
""")

st.success("You're ready to use the AI Governance Platform.")
