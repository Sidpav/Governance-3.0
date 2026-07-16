import streamlit as st
import pandas as pd

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

from llm.experiment_generator import generate_experiment

from database.project_execution_repository import (
    get_approved_projects,
    get_project,
    load_hypotheses,
    save_hypotheses,
)

from llm.stakeholder_summary import (
    generate_stakeholder_summary,
)

from llm.prototype_spec_generator import generate_prototype_spec

from llm.hypotheses_generator import generate_hypotheses

from llm.manual_hypothesis_generator import (
    generate_manual_hypothesis,
)

from utils.pdf_generator import generate_prototype_pdf

from database.project_execution_repository import (
    load_experiments,
    save_experiments,
    load_prototype_spec,

    save_prototype_spec,
)

from database.feedback_repository import (
    load_feedback_questions,
    save_feedback_questions,
    load_feedback,
    update_feedback,
    completed_stakeholders,
    save_feedback_summary,
    load_feedback_summary,
    load_consolidated_summary,
    save_consolidated_summary,
    all_feedback_complete,
    load_feedback_summaries,
)

from llm.feedback_summary import (
    generate_feedback_summary,
)

from llm.feedback_question_generator import (
    generate_feedback_questions,
)

from utils.feedback_pdf import (

    generate_stakeholder_summary_pdf,

    generate_committee_summary_pdf,

)

# ==========================================================
# PAGE SETUP
# ==========================================================

st.set_page_config(
    page_title="AI Product Delivery - Assumptions",
    page_icon="🧪",
    layout="wide",
)

require_login()

apply_theme()

render_sidebar(active="pe_assumptions")

render_navbar(active="pe_assumptions")

require_access("pe_assumptions")

render_breadcrumb(
    "AI Product Delivery",
    "Assumption & Hypothesis Register",
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "execution_state" not in st.session_state:
    st.session_state.execution_state = {
        "problem_id": None,
        "assumption_step": 1,
        "hypotheses": [],
        "experiment": {},
        "feedback": {},
    }

step = st.session_state.execution_state["assumption_step"]

if "editing_hypothesis" not in st.session_state:
    st.session_state.editing_hypothesis = None

if "editing_experiment" not in st.session_state:
    st.session_state.editing_experiment = None

# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🧪 Assumption & Hypothesis Register")

st.caption(
    "Validate project assumptions before implementation."
)

st.divider()

# ==========================================================
# PROJECT EXECUTION STEPPER
# ==========================================================

st.markdown("""
<style>

.pe-stepper{

    display:flex;

    justify-content:space-between;

    align-items:center;

    margin-bottom:35px;

}

.pe-step{

    flex:1;

    text-align:center;

}

.pe-step-name{

    font-size:1rem;

    font-weight:600;

    color:#64748B;

}

.pe-step-active{

    color:#6C63FF;

    font-weight:700;

}

.pe-line{

    flex:1;

    height:2px;

    background:#CBD5E1;

    margin:0 15px;

}

</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([4.5,.4,3.2,.4,4.2])

with c1:
    css = "pe-step-name pe-step-active" if step == 1 else "pe-step-name"
    st.markdown(
        f'<div class="{css}"><b>1</b>&nbsp; Assumption &amp; Hypothesis Register</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<hr style="margin-top:12px;">',
        unsafe_allow_html=True,
    )

with c3:
    css = "pe-step-name pe-step-active" if step == 2 else "pe-step-name"
    st.markdown(
        f'<div class="{css}"><b>2</b>&nbsp; Validation Plan</div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        '<hr style="margin-top:12px;">',
        unsafe_allow_html=True,
    )

with c5:
    css = "pe-step-name pe-step-active" if step == 3 else "pe-step-name"
    st.markdown(
        f'<div class="{css}"><b>3</b>&nbsp; Validation Evidence Upload</div>',
        unsafe_allow_html=True,
    )

st.divider()


# ==========================================================
# SELECT APPROVED PROJECT
# ==========================================================

st.subheader("Select Problem")

approved_projects = get_approved_projects()

if not approved_projects:

    st.warning(
        "No approved projects available.\n\n"
        "Approve a project from Governance Board first."
    )

    st.stop()

project_lookup = {
    p["problem_statement"]: p["id"]
    for p in approved_projects
}

selected_name = st.selectbox(
    "Approved Projects",
    list(project_lookup.keys()),
    index=None,
    placeholder="Select an approved project...",
    key="execution_project",
)

if selected_name:

    problem_id = project_lookup[selected_name]

    st.session_state.execution_state["problem_id"] = problem_id

    project = get_project(problem_id)

else:

    project = None

# ==========================================================
# PAGE CONTENT
# ==========================================================

if step == 1:

    # ==========================================================
    # PROJECT SUMMARY
    # ==========================================================

    st.subheader("Project Summary")

    if project:

        with st.container(border=True):

            st.markdown(f"### {project['problem_statement']}")

            c1, c2 = st.columns(2)

            with c1:

                st.markdown("**Business Objective**")

                st.write(project["business_objective"])

                st.markdown("**Timeline**")

                st.write(project.get("timeline") or "-")

                st.markdown("**Business Value**")

                st.write(project.get("business_value") or "-")

            with c2:

                st.markdown("**Owner**")

                st.write(project.get("action_owner") or "-")

                st.markdown("**Solution Approach**")

                st.write(project.get("solution_approach") or "-")

                st.markdown("**Workflow Location**")

                st.write(project.get("workflow_location") or "-")

    else:

        st.info("Select an approved project.")

    st.divider()

    generate = st.button(
        "✨ Generate Hypotheses",
        type="primary",
        disabled=(project is None),
        width='stretch',
    )

    if generate:

        with st.spinner("Generating hypotheses..."):

            hypotheses = generate_hypotheses(project)

            st.session_state.execution_state["hypotheses"] = hypotheses

            save_hypotheses(
                project["id"],
                hypotheses,
            )

            st.rerun()

    hypotheses = []

    if project:

        hypotheses = load_hypotheses(project["id"])

        if hypotheses:

            st.session_state.execution_state["hypotheses"] = hypotheses

    hypotheses = st.session_state.execution_state.get(
        "hypotheses",
        [],
    )

    if hypotheses:

        st.divider()

        st.subheader("Generated Hypotheses")

        for i, h in enumerate(hypotheses):

            review = h.get("expert_review", {})

            display_title = review.get("edited_title") or h.get("title", "Untitled Hypothesis")

            display_description = review.get("edited_description") or h.get("description", "")

            display_reasoning = review.get("edited_reasoning") or h.get("reasoning", "")

            display_metric = review.get("edited_metric") or h.get("success_metric", "")

            with st.container(border=True):

                # -----------------------------
                # Header badges
                # -----------------------------
                c1, c2, c3 = st.columns([6,1,1])

                with c1:
                    st.caption(
                        f"📘 {h.get('category','Business Hypothesis')}"
                    )

                with c2:
                    st.markdown(
                        f"<span style='background:#FEE2E2;"
                        "padding:4px 10px;"
                        "border-radius:12px;"
                        "font-size:12px;'>"
                        f"{h['priority']}</span>",
                        unsafe_allow_html=True
                    )

                with c3:
                    st.markdown(
                        "<span style='background:#EDE9FE;"
                        "padding:4px 10px;"
                        "border-radius:12px;"
                        "font-size:12px;'>"
                        f"{h.get('status','Proposed')}</span>",
                        unsafe_allow_html=True
                    )

                st.markdown(f"### {display_title}")

                st.markdown("#### Reasoning")

                st.info(display_reasoning)

                left, right = st.columns(2)

                with left:

                    st.markdown("##### What this tests")

                    st.info(display_description)

                with right:

                    st.markdown("##### Risk if wrong")

                    st.warning(h.get("risk_if_wrong",""))

                with st.expander("🤖 Why did Cortexa suggest this?"):

                    st.markdown("**Evidence from problem**")

                    st.write(h.get("evidence_problem",""))

                    st.markdown("**Evidence from documents**")

                    st.write(h.get("evidence_documents",""))

                    st.markdown("**Contradictions**")

                    st.write(h.get("contradictions",""))

                    st.markdown("**Business value dependency**")

                    st.write(h.get("business_dependency",""))

                    st.markdown("**Feasibility dependency**")

                    st.write(h.get("feasibility_dependency",""))

                    st.markdown("**Risk if not tested**")

                    st.write(h.get("risk_if_not_tested",""))

                expanded = (
                    st.session_state.editing_hypothesis == i
                )

                with st.expander(
                    "🧑‍💼 Domain Expert Review",
                    expanded=expanded,
                ):

                    review = h.setdefault("expert_review", {})

                    agreement_options = ["Yes", "Partially", "No"]

                    saved_agreement = review.get("agreement", "Yes")

                    if saved_agreement not in agreement_options:
                        saved_agreement = "Yes"

                    st.radio(
                        "Do you agree with this hypothesis?",
                        agreement_options,
                        horizontal=True,
                        index=agreement_options.index(saved_agreement),
                        key=f"agree_{i}",
                    )

                    st.text_input(
                        "Title",
                        value=review.get("edited_title", h["title"]),
                        key=f"edited_title_{i}"
                    )

                    st.text_area(
                        "Description",
                        value=review.get("edited_description", h["description"]),
                        key=f"edited_description_{i}"
                    )

                    st.text_area(
                        "Reasoning",
                        value=review.get("edited_reasoning", h.get("reasoning","")),
                        key=f"edited_reasoning_{i}"
                    )

                    st.text_input(
                        "Success Metric",
                        value=review.get("edited_metric", h.get("success_metric","")),
                        key=f"edited_metric_{i}"
                    )

                    st.text_area(
                        "Additional Assumption",
                        value=review.get("additional_assumption", h.get("additional_assumption", "")),
                        key=f"additional_{i}"
                    )

                    st.checkbox(
                        "Mark as critical",
                        value=review.get("critical", False),
                        key=f"critical_{i}"
                    )

                    st.text_area(
                        "Comments",
                        value=review.get("comments", ""),
                        key=f"comments_{i}"
                    )

                    if st.button(
                        "💾 Save",
                        key=f"save_review_{i}",
                    ):

                        review = {

                            "agreement":
                            st.session_state[f"agree_{i}"],

                            "edited_title":
                            st.session_state[f"edited_title_{i}"],

                            "edited_description":
                            st.session_state[f"edited_description_{i}"],

                            "edited_reasoning":
                            st.session_state[f"edited_reasoning_{i}"],

                            "edited_metric":
                            st.session_state[f"edited_metric_{i}"],

                            "additional_assumption":
                            st.session_state[f"additional_{i}"],

                            "critical":
                            st.session_state[f"critical_{i}"],

                            "comments":
                            st.session_state[f"comments_{i}"],
                        }

                        hypotheses[i]["expert_review"] = review

                        save_hypotheses(
                            project["id"],
                            hypotheses,
                        )

                        st.success("Review saved.")

                        st.session_state.editing_hypothesis = None

                        st.rerun()

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    if st.button(
                        "✏ Edit",
                        key=f"edit_btn_{i}",
                        width='stretch',
                    ):
                        st.session_state.editing_hypothesis = i
                        st.rerun()

                with c2:
                    if st.button(
                        "✅ Approve",
                        key=f"approve_{i}",
                        width='stretch',
                        disabled=(h.get("status") == "Approved"),
                    ):

                        review = {

                            "agreement": st.session_state[f"agree_{i}"],

                            "edited_title": st.session_state[f"edited_title_{i}"],

                            "edited_description": st.session_state[f"edited_description_{i}"],

                            "edited_reasoning": st.session_state[f"edited_reasoning_{i}"],

                            "edited_metric": st.session_state[f"edited_metric_{i}"],

                            "additional_assumption": st.session_state[f"additional_{i}"],

                            "critical": st.session_state[f"critical_{i}"],

                            "comments": st.session_state[f"comments_{i}"],

                        }

                        hypotheses[i]["expert_review"] = review

                        hypotheses[i]["status"] = "Approved"

                        save_hypotheses(
                            project["id"],
                            hypotheses,
                        )

                        st.session_state.editing_hypothesis = None

                        st.success("Hypothesis Approved.")

                        st.rerun()

                with c3:
                    if st.button(
                        "❌ Reject",
                        key=f"reject_{i}",
                        width='stretch',
                        disabled=(h.get("status") == "Rejected"),
                    ):

                        review = {

                            "agreement": st.session_state[f"agree_{i}"],

                            "edited_title": st.session_state[f"edited_title_{i}"],

                            "edited_description": st.session_state[f"edited_description_{i}"],

                            "edited_reasoning": st.session_state[f"edited_reasoning_{i}"],

                            "edited_metric": st.session_state[f"edited_metric_{i}"],

                            "additional_assumption": st.session_state[f"additional_{i}"],

                            "critical": st.session_state[f"critical_{i}"],

                            "comments": st.session_state[f"comments_{i}"],

                        }

                        hypotheses[i]["expert_review"] = review

                        hypotheses[i]["status"] = "Rejected"

                        save_hypotheses(
                            project["id"],
                            hypotheses,
                        )

                        st.session_state.editing_hypothesis = None

                        st.warning("Hypothesis Rejected.")

                        st.rerun()

                with c4:
                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{i}",
                        width='stretch',
                    ):
                        
                        if len(hypotheses) == 1:
                            st.error("At least one hypothesis must remain.")
                            st.stop()

                        hypotheses.pop(i)

                        save_hypotheses(
                            project["id"],
                            hypotheses,
                        )

                        st.success("Hypothesis Deleted")

                        st.rerun()

        st.divider()

        st.subheader("Add New Hypothesis")

        new_title = st.text_input(
            "Hypothesis Title",
            placeholder="Example: AI can reduce invoice approval delays by 40%",
        )

        if st.button(
            "➕ Add Hypothesis",
            type="primary",
            width='stretch',
        ):

            if not new_title.strip():

                st.warning("Enter a hypothesis title.")

            else:

                with st.spinner("Generating hypothesis..."):

                    titles = {

                        h["title"].lower()

                        for h in hypotheses

                    }

                    if new_title.lower() in titles:

                        st.error(
                            "A hypothesis with this title already exists."
                        )

                        st.stop()

                    new_hypothesis = generate_manual_hypothesis(

                        project,

                        new_title,

                        hypotheses,

                    )

                    hypotheses.append(new_hypothesis)

                    save_hypotheses(

                        project["id"],

                        hypotheses,

                    )

                    st.session_state.execution_state[
                        "hypotheses"
                    ] = hypotheses

                    st.success("New hypothesis added.")

                    st.rerun()

        if st.button(
                "🔄 Regenerate Hypotheses",
                width='stretch',
            ):

                with st.spinner("Generating..."):

                    hypotheses = generate_hypotheses(project)

                    save_hypotheses(
                        project["id"],
                        hypotheses,
                    )

                    st.session_state.execution_state["hypotheses"] = hypotheses

                    st.rerun()

        

elif step == 2:

    st.header("🧪 Experiment Design")

    hypotheses = load_hypotheses(project["id"])

    approved_hypotheses = [

        h

        for h in hypotheses

        if h.get("status") == "Approved"

    ]

    if not approved_hypotheses:

        st.warning("No approved hypotheses.")

        st.stop()

    experiments = load_experiments(project["id"])

    # -----------------------------------------
    # Generate missing experiments
    # -----------------------------------------

    experiments = load_experiments(project["id"])

    new_experiment_added = False

    for hypothesis in approved_hypotheses:

        exists = any(
            e.get("hypothesis_title") == hypothesis["title"]
            for e in experiments
        )

        if not exists:

            exp = generate_experiment(
                project,
                hypothesis,
            )

            exp["hypothesis_title"] = hypothesis["title"]

            experiments.append(exp)

            new_experiment_added = True


    if new_experiment_added:

        save_experiments(
            project["id"],
            experiments,
        )

    

    st.subheader("Experiment Summary")

    summary = []

    for exp in experiments:

        summary.append({

            "Hypothesis":
                exp["hypothesis_title"],

            "Suggested Experiment":
                exp["title"],

            "Required Data":
                exp["required_data"],

            "Success Criteria":
                exp["success_criteria"],

            "Owner":
                exp["owner"]

        })

    st.dataframe(

        pd.DataFrame(summary),

        width='stretch',

        hide_index=True,

    )

    st.divider()

    st.subheader("Generated Experiments")

    for i, exp in enumerate(experiments):

        with st.expander(
            exp["title"],
            expanded=(i == 0),
        ):

            st.caption(exp["hypothesis_title"])

            status = exp.get("status","Proposed")

            if status == "Approved":
                st.success("Status: Approved")

            elif status == "Rejected":
                st.error("Status: Rejected")

            else:
                st.info("Status: Proposed")

            # ---------------- Row 1 ----------------

            c1, c2 = st.columns(2)

            with c1:

                st.info(
                    f"### METHOD\n\n"
                    f"{exp['methodology']}"
                )

            with c2:

                st.info(
                    f"### REQUIRED DATA\n\n"
                    f"{exp['required_data']}"
                )

            # ---------------- Row 2 ----------------

            c1, c2 = st.columns(2)

            with c1:

                st.info(
                    f"### SUCCESS CRITERIA\n\n"
                    f"{exp['success_criteria']}"
                )

            with c2:

                st.info(
                    f"### FAILURE CRITERIA\n\n"
                    f"{exp['failure_criteria']}"
                )

            # ---------------- Row 3 ----------------

            c1, c2 = st.columns(2)

            with c1:

                st.info(
                    f"### DECISION RULE\n\n"
                    f"{exp['decision_rule']}"
                )

            with c2:

                st.info(
                    f"### RISK\n\n"
                    f"{exp['risks']}"
                )

            st.markdown(
                f"**Owner:** {exp['owner']} &nbsp;&nbsp;&nbsp;&nbsp;"
                f"**Timeline:** {exp['timeline']}",
                unsafe_allow_html=True,
            )

            st.divider()

            st.markdown("### Upload Experiment Results & Analysis")

            st.file_uploader(
                "Upload experiment evidence",
                key=f"upload_{i}",
                type=["pdf","docx","ppt","pptx","txt"],
                label_visibility="collapsed",
            )

            st.divider()

            expanded = (
                st.session_state.editing_experiment == i
            )

            b1, b2, b3, b4 = st.columns(4)

            with b1:

                if st.button(
                    "✅ Approve",
                    key=f"approve_exp_{i}",
                    width='stretch',
                    disabled=(exp.get("status")=="Approved"),
                ):

                    experiments[i]["status"]="Approved"

                    save_experiments(
                        project["id"],
                        experiments,
                    )

                    st.success("Experiment approved.")

                    st.rerun()

            with b2:

                if st.button(
                    "❌ Reject",
                    key=f"reject_exp_{i}",
                    width='stretch',
                    disabled=(exp.get("status")=="Rejected"),
                ):

                    experiments[i]["status"]="Rejected"

                    save_experiments(
                        project["id"],
                        experiments,
                    )

                    st.warning("Experiment rejected.")

                    st.rerun()

            with b3:

                if st.button(
                    "💬 Comment",
                    key=f"comment_exp_{i}",
                    width='stretch',
                ):
                    with st.expander(
                        "Reviewer Comments",
                        expanded=expanded,
                    ):

                        review = exp.setdefault("expert_review", {})

                        st.text_area(
                            "Comments",
                            value=review.get("comments",""),
                            key=f"exp_comment_{i}",
                        )

                        if st.button(
                            "💾 Save Comment",
                            key=f"save_comment_{i}",
                        ):

                            review["comments"] = st.session_state[f"exp_comment_{i}"]

                            experiments[i]["expert_review"] = review

                            save_experiments(
                                project["id"],
                                experiments,
                            )

                            st.session_state.editing_experiment = None

                            st.success("Comment saved.")

                            st.rerun()

            with b4:

                if st.button(
                    "✔ Mark Ready",
                    key=f"ready_exp_{i}",
                    width='stretch',
                ):

                    review = exp.setdefault("expert_review", {})

                    review["ready"] = True

                    experiments[i]["expert_review"] = review

                    save_experiments(
                        project["id"],
                        experiments,
                    )

                    st.success("Experiment marked ready.")

                    st.rerun()

    prototype_spec=load_prototype_spec(

        project["id"]

    )

    if prototype_spec:

        st.divider()

        st.header("Prototype Specification Document")

        sections=[

        ("Architecture Design","architecture_design"),

        ("Technical Details","technical_details"),

        ("Implementation Plan","implementation_plan"),

        ("Data & Features","data_features"),

        ("Models Used","models_used"),

        ("Model Validation","model_validation"),

        ("Results Analysis","results_analysis"),

        ("Infrastructure","infrastructure"),

        ("Security","security"),

        ("Deployment","deployment"),

        ("Maintenance","maintenance"),

        ("Future Scope","future_scope"),

        ]

        pdf_bytes = generate_prototype_pdf(prototype_spec)
        st.download_button("⬇ Download PDF", data=pdf_bytes,
                           file_name=f"{project['id']}_Prototype_Specification.pdf",
                           mime="application/pdf")

        for i,(title,key) in enumerate(sections,1):

            with st.expander(

                f"{i}. {title}",

                expanded=(i==1),

            ):

                st.write(

                    prototype_spec.get(key,"")

                )

elif step == 3:

    st.header("📋 Prototype Feedback")

    prototype_spec = load_prototype_spec(
        project["id"]
    )

    hypotheses = load_hypotheses(
        project["id"]
    )

    experiments = load_experiments(
        project["id"]
    )

    approved_experiments = [
        e
        for e in experiments
        if e.get("status") == "Approved"
    ]

    questions = load_feedback_questions(
        project["id"]
    )

    if questions is None:

        with st.spinner(
            "Generating stakeholder questionnaires..."
        ):

            questions = generate_feedback_questions(

                project,

                hypotheses,

                approved_experiments,

                prototype_spec,

            )

            save_feedback_questions(

                project["id"],

                questions,

            )

            st.rerun()

    feedback = load_feedback(project["id"])

    completed = completed_stakeholders(
        project["id"]
    )

    options = []

    for stakeholder in questions["stakeholders"]:

        role = stakeholder["role"]

        if role in completed:

            options.append(f"✅ {role}")

        else:

            options.append(role)

    selected = st.selectbox(

        "Stakeholder",

        options,

        width="stretch",

    )

    current_role = selected.replace("✅ ", "")

    current = next(

        s

        for s in questions["stakeholders"]

        if s["role"] == current_role

    )

    st.info(

        f"""
    ### {current['role']}

    **Objective**

    {current['objective']}
    """
    )

    col1, col2 = st.columns(2)

    with col1:

        reviewer = st.text_input(
            "Reviewer"
        )

    with col2:

        review_date = st.date_input(
            "Review Date"
        )

    answers = []

    total_questions = sum(
        len(section["questions"])
        for section in current["sections"]
    )

    answered_questions = sum(
        1
        for a in answers
        if a.get("score")
    )

    for section in current["sections"]:

        with st.expander(

            section["title"],

            expanded=True,

        ):

            for question in section["questions"]:

                st.markdown(
                    f"**{question['question']}**"
                )

                score = st.radio(
                    "Rating",
                    [
                        "",
                        "Strongly Agree",
                        "Agree",
                        "Neutral",
                        "Disagree",
                        "Strongly Disagree",
                    ],
                    index=0,
                    format_func=lambda x: "" if x == "" else x,
                    horizontal=True,
                    key=f"{current_role}_{question['question']}"
                )

                c1, c2 = st.columns(2)

                with c1:

                    blocker = st.checkbox(
                        "Blocker",
                        key=f"{current_role}_{question['question']}_blocker",
                    )

                with c2:

                    evidence_required = st.checkbox(
                        "Evidence Required",
                        key=f"{current_role}_{question['question']}_evidence_required",
                    )

                comment = st.text_area(
                    "Comment",
                    placeholder="Enter your comments...",
                    key=f"{current_role}_{question['question']}_comment",
                )

                answers.append({

                    "question": question["question"],

                    "score": None if score == "" else score,

                    "blocker": blocker,

                    "evidence_required": evidence_required,

                    "comment": comment,

                })
            
    answered_questions = sum(
        1
        for a in answers
        if a["score"] is not None
    )

    progress = answered_questions / total_questions

    st.divider()

    st.markdown("### Progress")

    st.progress(
        progress,
        text=f"{answered_questions}/{total_questions} Questions Answered",
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        blockers = sum(
            a["blocker"]
            for a in answers
        )

        st.metric(
            "Blockers",
            blockers,
        )

    with col2:

        evidence = sum(
            1
            for a in answers
            if a["evidence_required"]
        )

        st.metric(
            "Evidence",
            evidence,
        )

    with col3:

        completion = int(
            progress * 100
        )

        st.metric(
            "Completion",
            f"{completion}%"
        )

    st.subheader("Supporting Documents")

    supporting_docs = st.file_uploader(
        "Upload feedback documents",
        accept_multiple_files=True,
    )

    st.subheader("Final Decision")

    decision = st.radio(
        "Prototype Recommendation",
        [
            "Infrastructure Ready",
            "Ready with Restrictions",
            "Requires Integration Work",
            "Requires Security Review",
            "Not Ready for MVP",
        ],
        horizontal=True,
    )
    
    st.divider()

    if st.button(

        "Submit Feedback",

        key=f"submit_{current_role}",

        type="primary",

        width='stretch',

    ):
                
        review = {
            "stakeholder": current_role,
            "reviewer": reviewer,
            "review_date": str(review_date),
            "decision": decision,
            "submitted": True,
            "answers": answers,
        }

        review["documents"] = []

        if supporting_docs:

            review["documents"] = [
                file.name
                for file in supporting_docs
            ]

        update_feedback(

            project["id"],

            current_role,

            review,

        )

        summary = generate_stakeholder_summary(

            project,

            prototype_spec,

            current_role,

            review,

        )

        save_feedback_summary(

            project["id"],

            current_role,

            summary,

        )

        if all_feedback_complete(project["id"]):

            overall = load_consolidated_summary(
                project["id"]
            )

            if not overall:

                overall = generate_feedback_summary(

                    project,

                    prototype_spec,

                    load_feedback_summaries(
                        project["id"]
                    ),

                )

                save_consolidated_summary(

                    project["id"],

                    overall,

                )

        st.success(
            "Feedback submitted."
        )

    summary = load_feedback_summary(

        project["id"],

        current_role,

    )

    if summary:

        st.divider()

        st.subheader("Stakeholder Summary")

        rows=[

            ("Product View",summary["product_view"]),

            ("Data View",summary["data_view"]),

            ("Compliance View",summary["compliance_view"]),

            ("Business View",summary["business_view"]),

            ("Infrastructure View",summary["infrastructure_view"]),

            ("Overall Decision",summary["overall_decision"]),

            ("MVP Recommendation",summary["mvp_recommendation"]),

            ("Blockers",summary["blockers"]),

            ("Confidence",summary["confidence"]),

        ]

        for title, value in rows:
            st.markdown(f"### {title}")
            st.write(value)

        pdf_bytes = generate_stakeholder_summary_pdf(current_role, summary)
        st.download_button("⬇ Download Stakeholder Summary", pdf_bytes,
                           file_name=f"{project['id']}_{current_role}_Summary.pdf",
                           mime="application/pdf")

    overall = {}

    if all_feedback_complete(project["id"]):

        overall = load_consolidated_summary(
            project["id"]
        )

    if overall:

        st.write(
            overall["feedback_summary"]
        )

        st.subheader("Agreement Areas")

        for item in overall["agreement_areas"]:
            st.success(item)

        st.subheader("Disagreement Areas")

        for item in overall["disagreement_areas"]:
            st.warning(item)

        st.subheader("Feature Changes Required")

        for item in overall["feature_changes_required"]:
            st.info(item)

        st.subheader("Risks Raised")

        for item in overall["risks_raised"]:
            st.error(item)

        st.subheader("Recommended MVP Scope")

        st.write(
            overall["recommended_mvp_scope"]
        )

        committee_pdf = generate_committee_summary_pdf(overall)
        st.download_button("⬇ Download Governance Committee Report", committee_pdf,
                           file_name=f"{project['id']}_Governance_Committee_Report.pdf",
                           mime="application/pdf")


st.write("")

st.divider()

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

if step == 1:

    left, middle, right = st.columns([1,5,1])

elif step == 2:

    left, prototype, right = st.columns([1,2,1])

else:

    left, middle, right = st.columns([1,5,1])


# ---------------- Back ----------------

with left:

    if step > 1:

        if st.button(
            "← Back",
            width='stretch',
        ):

            st.session_state.execution_state["assumption_step"] -= 1
            st.rerun()


# ---------------- Prototype Button ----------------

if step == 2:

    with prototype:

        approved_experiments = [
            e for e in experiments
            if e.get("status") == "Approved"
        ]

        if st.button(
            "✨ Generate Prototype Specs",
            width='stretch',
            disabled=len(approved_experiments) == 0,
        ):

            spec = generate_prototype_spec(
                project,
                approved_experiments,
            )

            save_prototype_spec(
                project["id"],
                spec,
            )

            st.rerun()


# ---------------- Next ----------------

with right:

    if step < 3:

        if st.button(
            "Next →",
            type="primary",
            width='stretch',
        ):

            st.session_state.execution_state["assumption_step"] += 1
            st.rerun()

    else:

        if st.button(
            "Proceed to Data →",
            type="primary",
            width='stretch',
        ):

            st.switch_page("pages/8_PE_Data.py")
