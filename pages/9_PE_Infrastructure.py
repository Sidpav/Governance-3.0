import streamlit as st

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

from database.project_execution_repository import (
    get_approved_projects,
    load_hypotheses,
    load_experiments,
    load_prototype_spec,
)

from database.infrastructure_repository import (
    load_infrastructure_review,
    save_infrastructure_review,
    load_infrastructure_output,
    save_infrastructure_output,
    update_review,
    update_security_answer,
    load_security_questions,
    save_security_questions,
)

from llm.security_question_generator import(
    generate_security_questions,
)

from llm.infrastructure_recommendation_generator import (
    generate_infrastructure_recommendation,
)

from llm.infrastructure_output_generator import (
    generate_infrastructure_output,
)

st.set_page_config(
    page_title="AI Product Delivery - Infrastructure",
    page_icon="🏗️",
    layout="wide",
)

require_login()

apply_theme()

render_sidebar(active="pe_infrastructure")

render_navbar(active="pe_infrastructure")

require_access("pe_infrastructure")

render_breadcrumb(
    "AI Product Delivery",
    "Infrastructure",
)

st.title("🏗️ Infrastructure")

st.caption(
    "Review infrastructure requirements and deployment recommendations."
)

st.divider()

projects = get_approved_projects()

if not projects:

    st.warning(
        "No approved projects found."
    )

    st.stop()

project_map = {

    f"{p['id']} - {p['problem_statement']}": p

    for p in projects

}

selected = st.selectbox(

    "Select Project",

    list(project_map.keys()),

    width="stretch",

)

project = project_map[selected]

prototype_spec = load_prototype_spec(
    project["id"]
)

if not prototype_spec:

    st.warning(
        "Prototype specification not found."
    )

    st.stop()

hypotheses = [

    h

    for h in load_hypotheses(project["id"])

    if h.get("status") == "Approved"

]

experiments = [

    e

    for e in load_experiments(project["id"])

    if e.get("status") == "Approved"

]

review = load_infrastructure_review(
    project["id"]
)

output = load_infrastructure_output(
    project["id"]
)

if "infra_step" not in st.session_state:

    st.session_state.infra_step = 1

step = st.session_state.infra_step

if step == 1:

    st.header("Infrastructure Decision Intake")

    st.caption(
        "Stakeholders: Infrastructure Lead · Business Owner · Data Team"
    )

    st.divider()

    def decision(
        question,
        key,
        options,
    ):

        cols = st.columns([6, 3])

        with cols[0]:

            st.write(question)

        with cols[1]:

            current = review.get(
                key,
                options[0],
            )

            value = st.segmented_control(

                "Value",

                options,

                default=current,

                key=key,

                label_visibility="collapsed",

            )

        if value:

            update_review(
                project["id"],
                key,
                value,
            )

    decision(

        "Will the solution use a closed LLM or open LLM?",

        "llm_type",

        [

            "Closed LLM",

            "Open LLM",

            "Both",

            "TBD",

        ],

    )

    decision(

        "Will deployment be cloud, on-prem, or hybrid?",

        "deployment",

        [

            "Cloud",

            "On-Prem",

            "Hybrid",

            "TBD",

        ],

    )

    decision(

        "Is the use case batch, near-real-time, or real-time?",

        "processing",

        [

            "Batch",

            "Near-Real-Time",

            "Real-Time",

        ],

    )

    decision(

        "Is the usage continuous or seasonal/spike-based?",

        "usage",

        [

            "Continuous",

            "Spike-Based",

            "Seasonal",

        ],

    )

    decision(

        "Does training or fine-tuning happen?",

        "training",

        [

            "Yes",

            "No",

            "Later",

        ],

    )

    decision(

        "Is this RAG-only, fine-tuning, or hybrid?",

        "architecture",

        [

            "RAG Only",

            "Fine-Tuning",

            "Hybrid",

            "Neither",

        ],

    )

    decision(

        "Is customer data confidential?",

        "confidential",

        [

            "Yes",

            "No",

            "Partially",

        ],

    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        users = st.number_input(

            "Expected users in Phase 1",

            min_value=1,

            value=review.get(
                "users",
                50,
            ),

        )

        update_review(

            project["id"],

            "users",

            users,

        )

    with c2:

        requests = st.number_input(

            "Expected requests per day",

            min_value=1,

            value=review.get(
                "requests_per_day",
                200,
            ),

        )

        update_review(

            project["id"],

            "requests_per_day",

            requests,

        )

    st.divider()

    _, right = st.columns([6, 2])

    with right:

        if st.button(

            "Show AI Recommendation →",

            width='stretch',

        ):

            st.session_state.infra_step = 2

            st.rerun()

elif step == 2:

    st.header("Model & Compute Recommendation")

    st.caption(
        "AI-generated infrastructure recommendations based on project requirements."
    )

    st.divider()

    recommendation = output.get("recommendation")

    if recommendation is None:

        with st.spinner(
            "Generating Infrastructure Recommendation..."
        ):

            recommendation = generate_infrastructure_recommendation(

                project,

                hypotheses,

                experiments,

                prototype_spec,

                review,

            )

            output["recommendation"] = recommendation

            save_infrastructure_output(

                project["id"],

                output,

            )

            st.rerun()

    st.subheader("Recommendation Summary")

    summary = []

    for row in recommendation["recommendations"]:

        summary.append({

            "Area": row["area"],

            "Recommendation": row["recommendation"],

            "Reason": row["reason"],

        })

    st.dataframe(

        summary,

        hide_index=True,

        width='stretch',

    )

    st.divider()

    st.subheader("Detailed Recommendations")

    for row in recommendation["recommendations"]:

        with st.container(border=True):

            st.markdown(
                f"### {row['area']}"
            )

            st.success(
                row["recommendation"]
            )

            st.write(
                row["reason"]
            )

    st.divider()

    left, right = st.columns(2)

    with left:

        if st.button(

            "← Back",

            width='stretch',

        ):

            st.session_state.infra_step = 1

            st.rerun()

    with right:

        if st.button(

            "Next → Security Review",

            width='stretch',

        ):

            st.session_state.infra_step = 3

            st.rerun()

elif step == 3:

    st.header("Security Review")

    st.caption(
        "Review security, privacy and governance controls before infrastructure approval."
    )

    st.divider()

    questions = load_security_questions(
        project["id"]
    )

    recommendation = output.get("recommendation")

    if recommendation is None:

        st.warning(
            "Generate the infrastructure recommendation first."
        )

        st.stop()

    if questions is None:

        with st.spinner(
            "Generating Security Questions..."
        ):

            questions = generate_security_questions(

                project,

                prototype_spec,

                review,

                recommendation,

            )

            save_security_questions(

                project["id"],

                questions,

            )

            st.rerun()

    header = st.columns([7,2])

    header[0].markdown("**Security Question**")
    header[1].markdown("**Answer**")
    security_answers = {}

    for i, item in enumerate(
        questions["security_questions"]
    ):

        category = item["category"]

        question = item["question"]

        row = st.columns([7, 2])

        with row[0]:

            st.caption(category)

            st.write(question)

        with row[1]:

            current = review.get(
                "security",
                {}
            ).get(
                question,
                "Yes",
            )

            answer = st.selectbox(

                "Answer",

                [

                    "Yes",

                    "No",

                    "Partial",

                ],

                index=[
                    "Yes",
                    "No",
                    "Partial",
                ].index(current),

                key=f"security_{i}",

                label_visibility="collapsed",

            )

            security_answers[question] = answer

            update_security_answer(

                project["id"],

                question,

                answer,

            )

    st.divider()

    yes_count = list(security_answers.values()).count("Yes")
    partial_count = list(security_answers.values()).count("Partial")
    no_count = list(security_answers.values()).count("No")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Yes",
        yes_count,
    )

    c2.metric(
        "Partial",
        partial_count,
    )

    c3.metric(
        "No",
        no_count,
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        if st.button(

            "← Back",

            width='stretch',

        ):

            st.session_state.infra_step = 2

            st.rerun()

    with right:

        if st.button(

            "Next → Infrastructure Output",

            width='stretch',

        ):

            st.session_state.infra_step = 4

            st.rerun()

elif step == 4:

    st.header("Infrastructure Output")

    st.caption(
        "Final infrastructure recommendation generated using all previous decisions."
    )

    st.divider()

    recommendation = output.get("recommendation")

    final_output = output.get("final_output")

    if final_output is None:

        with st.spinner(
            "Generating Infrastructure Output..."
        ):

            final_output = generate_infrastructure_output(

                project,

                prototype_spec,

                recommendation,

                review.get(
                    "security",
                    {}
                ),

            )

            output["final_output"] = final_output

            save_infrastructure_output(

                project["id"],

                output,

            )

            st.rerun()

    with st.container(border=True):

        st.subheader("Deployment Recommendation")

        st.write(
            final_output["deployment_recommendation"]
        )

    with st.container(border=True):

        st.subheader("Training Requirement")

        st.write(
            final_output["training_requirement"]
        )

    with st.container(border=True):

        st.subheader("Inference Requirement")

        st.write(
            final_output["inference_requirement"]
        )

    with st.container(border=True):

        st.subheader("Compute Estimate")

        st.write(
            final_output["compute_estimate"]
        )

    with st.container(border=True):

        st.subheader("Storage Estimate")

        st.write(
            final_output["storage_estimate"]
        )

    with st.container(border=True):

        st.subheader("Security Controls")

        st.write(
            final_output["security_controls"]
        )

    with st.container(border=True):

        st.subheader("Data Access Restrictions")

        st.write(
            final_output["data_access_restrictions"]
        )

    with st.container(border=True):

        st.subheader("Estimated Monthly Cost")

        st.write(
            final_output["estimated_monthly_cost"]
        )

    st.divider()

    decision = st.radio(

        "Infrastructure Decision",

        [

            "Approved",

            "Approved with Conditions",

            "Requires Further Review",

        ],

        horizontal=True,

    )

    comments = st.text_area(

        "Reviewer Comments",

        placeholder="Enter comments...", 

    )

    if st.button(

        "Save Infrastructure Output",

        type="primary",

        width='stretch',

    ):

        output["decision"] = decision

        output["comments"] = comments

        save_infrastructure_output(

            project["id"],

            output,

        )

        st.success(
            "Infrastructure review saved successfully."
        )

    st.divider()

    left, right = st.columns(2)

    with left:

        if st.button(

            "← Back",

            width='stretch',

        ):

            st.session_state.infra_step = 3

            st.rerun()

    with right:

        if st.button(

            "Proceed → Workflow",

            width='stretch',

        ):

            st.switch_page(
                "pages/10_PE_Workflow.py"
            )
