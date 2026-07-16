import copy
import hashlib
import io

import pandas as pd
import streamlit as st

from database.data_repository import (
    load_data_requirements,
    load_data_review,
    save_data_requirements,
    save_data_review,
)
from database.delivery_repository import load_assignments
from database.project_execution_repository import (
    get_approved_projects,
    load_experiments,
    load_hypotheses,
    load_prototype_spec,
)
from llm.data_generator import generate_data_requirements
from ui.auth import require_access, require_login
from ui.navbar import render_breadcrumb, render_navbar
from ui.sidebar import render_sidebar
from ui.theme import apply_theme


st.set_page_config(page_title="AI Product Delivery - Data", page_icon="🗄️", layout="wide")
require_login()
apply_theme()
render_sidebar(active="pe_data")
render_navbar(active="pe_data")
require_access("pe_data")
render_breadcrumb("AI Product Delivery", "Data")


GROUP_COLORS = {
    "blue": ("#E7F0FF", "#155EEF", "#A8CAFF"),
    "red": ("#FFE8EC", "#C8103D", "#FFC1CD"),
    "purple": ("#F3E7FF", "#8116D7", "#E4C2FF"),
    "orange": ("#FFF3D6", "#B95000", "#FFD96B"),
    "green": ("#DDF9ED", "#087A55", "#8FE9C5"),
}
TRUST_OPTIONS = ["— Select —", "Human", "System", "Partial", "Mixed", "Subjective", "Standardized", "Yes", "No"]
ANSWER_OPTIONS = ["Yes", "No", "Partial"]


def _key(*parts):
    value = "|".join(str(part) for part in parts)
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:14]


def _fallback_requirements():
    """Safe editable baseline if the LLM is unavailable."""
    return {
        "structured_data": [
            {"group": "Business Entities", "color": "blue", "categories": [
                {"name": "Identity & Ownership", "attributes": ["Primary entity record", "Business owner"]},
                {"name": "Segmentation", "attributes": ["Entity segment"]},
            ]},
            {"group": "Transactions & Outcomes", "color": "red", "categories": [
                {"name": "Transactions", "attributes": ["Transaction history", "Transaction date"]},
                {"name": "Outcomes", "attributes": ["Decision outcome", "Outcome date"]},
            ]},
            {"group": "Product Engagement", "color": "purple", "categories": [
                {"name": "Usage Metrics", "attributes": ["Product usage metrics"]},
            ]},
            {"group": "Support & Exceptions", "color": "orange", "categories": [
                {"name": "Volume & Escalation", "attributes": ["Support ticket count", "Escalation count"]},
                {"name": "Classification", "attributes": ["Issue category"]},
            ]},
        ],
        "unstructured_data": [
            {"group": "Stakeholder Communications", "color": "blue", "categories": [
                {"name": "Direct Contact", "sources": ["Emails", "Meeting transcripts"]},
                {"name": "Feedback Channels", "sources": ["Survey comments", "Free-text responses"]},
            ]},
            {"group": "Business Activity", "color": "green", "categories": [
                {"name": "Account Records", "sources": ["Review notes", "Decision notes"]},
                {"name": "Product Feedback", "sources": ["Product feedback notes"]},
            ]},
            {"group": "Support Records", "color": "orange", "categories": [
                {"name": "Tickets & Complaints", "sources": ["Support ticket text", "Complaint descriptions"]},
            ]},
        ],
        "data_leakage_questions": [
            "Are any fields only known after the predicted event has occurred?",
            "Are final outcomes being used as model inputs?",
            "Are post-event notes included in training data?",
            "Are outcome labels accidentally included in the feature set?",
        ],
        "data_quality_questions": [
            "Are entity identifiers consistent across all source systems?",
            "Are duplicate records present in any source system?",
            "Are names and categories standardized across systems?",
            "Are manually entered reasons captured consistently?",
            "Are missing values and outliers monitored?",
        ],
        "topic_coverage": [
            "Business objective", "User needs", "Process exceptions", "Risk indicators",
            "Operational impact", "Compliance concerns", "Failure modes", "Human overrides",
            "Performance feedback", "Stakeholder sentiment",
        ],
    }


def _normalise_requirements(raw):
    base = _fallback_requirements()
    if not isinstance(raw, dict):
        return base
    result = copy.deepcopy(raw)
    for key in ("structured_data", "unstructured_data", "data_leakage_questions", "data_quality_questions", "topic_coverage"):
        if not isinstance(result.get(key), list) or not result[key]:
            result[key] = copy.deepcopy(base[key])
    for index, group in enumerate(result["structured_data"]):
        group.setdefault("group", f"Structured Group {index + 1}")
        group.setdefault("color", list(GROUP_COLORS)[index % len(GROUP_COLORS)])
        group.setdefault("categories", [])
    for index, group in enumerate(result["unstructured_data"]):
        group.setdefault("group", f"Unstructured Group {index + 1}")
        group.setdefault("color", list(GROUP_COLORS)[index % len(GROUP_COLORS)])
        group.setdefault("categories", [])
    return result


def _hierarchy(groups, item_key):
    st.markdown('<div class="dr-card"><h3>Required %s Data Sources</h3>' % (
        "Structured" if item_key == "attributes" else "Unstructured"
    ), unsafe_allow_html=True)
    for group_index, group in enumerate(groups):
        bg, fg, line = GROUP_COLORS.get(group.get("color", "blue"), GROUP_COLORS["blue"])
        st.markdown(
            f'<div class="dr-group-label" style="background:{bg};color:{fg};border-color:{line}">{group["group"]}</div>'
            f'<div class="dr-tree" style="border-color:{line}">', unsafe_allow_html=True,
        )
        for category in group.get("categories", []):
            st.markdown(f'<div class="dr-category">↳ {category.get("name", "General")}</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="dr-chip">{item}</span>' for item in category.get(item_key, []))
            st.markdown(f'<div class="dr-chips">{chips}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _add_rows_from_csv(requirements, uploaded, structured):
    frame = pd.read_csv(io.BytesIO(uploaded.getvalue()))
    columns = {str(c).strip().lower(): c for c in frame.columns}
    if "name" not in columns:
        raise ValueError("CSV must include a Name column.")
    for _, row in frame.iterrows():
        name = str(row[columns["name"]]).strip()
        if not name or name.lower() == "nan":
            continue
        category = str(row[columns.get("category", columns["name"])]).strip() if "category" in columns else "Imported"
        group_name = str(row[columns.get("type", columns["name"])]).strip() if "type" in columns else "Imported"
        collection = requirements["structured_data" if structured else "unstructured_data"]
        group = next((g for g in collection if g.get("group") == group_name), None)
        if group is None:
            group = {"group": group_name, "color": "blue" if structured else "green", "categories": []}
            collection.append(group)
        cat = next((c for c in group["categories"] if c.get("name") == category), None)
        if cat is None:
            cat = {"name": category, "attributes" if structured else "sources": []}
            group["categories"].append(cat)
        target = cat["attributes" if structured else "sources"]
        if name not in target:
            target.append(name)


def _add_upload_panel(project_id, requirements, structured):
    noun = "Feature" if structured else "Source"
    st.markdown(f"### Add / Upload {noun}s")
    st.caption(
        f"Manually add a {noun.lower()} or upload a CSV file "
        f"(columns: Name, Category, Type, Description)"
    )
    upload_col, manual_col = st.columns(2)
    with upload_col:
        uploaded = st.file_uploader(f"Upload {noun} CSV", type=["csv"], key=f"csv_{noun}")
        if uploaded and st.button(f"Import {noun}s", key=f"import_{noun}"):
            try:
                _add_rows_from_csv(requirements, uploaded, structured)
                save_data_requirements(project_id, requirements)
                st.success(f"{noun}s imported successfully.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with manual_col:
        with st.expander(f"＋ Add {noun}"):
            with st.form(f"manual_{noun}", clear_on_submit=True):
                name = st.text_input(f"{noun} name")
                category = st.text_input("Category", value="General")
                group_name = st.text_input("Type / group", value="Custom")
                description = st.text_area("Description")
                submitted = st.form_submit_button(f"Add {noun}", type="primary")
            if submitted:
                if not name.strip():
                    st.error(f"Enter a {noun.lower()} name.")
                else:
                    collection = requirements["structured_data" if structured else "unstructured_data"]
                    group = next((g for g in collection if g.get("group") == group_name.strip()), None)
                    if group is None:
                        group = {"group": group_name.strip(), "color": "blue" if structured else "green", "categories": []}
                        collection.append(group)
                    cat = next((c for c in group["categories"] if c.get("name") == category.strip()), None)
                    if cat is None:
                        cat = {"name": category.strip(), "attributes" if structured else "sources": []}
                        group["categories"].append(cat)
                    cat["attributes" if structured else "sources"].append(name.strip())
                    save_data_requirements(project_id, requirements)
                    st.success(f"{noun} added.")
                    st.rerun()


def _question_block(title, questions, review, review_key, project_id, warning=None):
    with st.container(border=True):
        st.markdown(f"### {title}")
        if warning:
            st.warning(warning, icon="⚠️")
        answers = review.setdefault(review_key, {})
        for index, question in enumerate(questions):
            row = st.columns([6, 2])
            row[0].markdown(question)
            saved = answers.get(question)
            answer = row[1].radio(
                "Answer", ANSWER_OPTIONS,
                index=ANSWER_OPTIONS.index(saved) if saved in ANSWER_OPTIONS else None,
                horizontal=True, label_visibility="collapsed",
                key=f"{review_key}_{_key(project_id, index, question)}",
            )
            if answer:
                answers[question] = answer


def _render_structured(project_id, requirements, review):
    st.markdown("### STAKEHOLDERS: &nbsp; `Data Team` &nbsp; `Tech Team`")
    _hierarchy(requirements["structured_data"], "attributes")

    attributes = []
    for group in requirements["structured_data"]:
        for category in group.get("categories", []):
            for attribute in category.get("attributes", []):
                attributes.append((group["group"], category.get("name", "General"), attribute))

    with st.container(border=True):
        confirmed = sum(bool(review.get("attributes", {}).get(f"{g}|{c}|{a}", {}).get("available")) for g, c, a in attributes)
        head1, head2 = st.columns([5, 2])
        head1.markdown("### Attribute Availability & Missing Data")
        head2.markdown(f'<div class="dr-count">{confirmed}/{len(attributes)} confirmed available</div>', unsafe_allow_html=True)
        st.progress(confirmed / len(attributes) if attributes else 0)
        header = st.columns([5, 1.2, 3.3])
        header[0].markdown("**Attribute**")
        header[1].markdown("**Available**")
        header[2].markdown("**Missing Data %**")
        attribute_review = review.setdefault("attributes", {})
        for group_name, category_name, attribute in attributes:
            attr_id = f"{group_name}|{category_name}|{attribute}"
            # Read the legacy attribute-only key when upgrading an existing
            # project, then persist the collision-safe composite key.
            saved = attribute_review.get(attr_id, attribute_review.get(attribute, {}))
            row = st.columns([5, 1.2, 3.3])
            row[0].markdown(f"**{attribute}**")
            available = row[1].checkbox("Available", value=bool(saved.get("available", False)), label_visibility="collapsed", key=f"av_{_key(project_id, attr_id)}")
            missing = row[2].slider("Missing Data %", 0, 100, int(saved.get("missing_percent", 0)), disabled=not available, label_visibility="collapsed", key=f"miss_{_key(project_id, attr_id)}")
            attribute_review[attr_id] = {"available": available, "missing_percent": missing}

    with st.container(border=True):
        _add_upload_panel(project_id, requirements, structured=True)

    _question_block(
        "C. Data Leakage Questions ⚠️", requirements["data_leakage_questions"],
        review, "leakage", project_id,
        "Leakage fields invalidate model results. Answer carefully.",
    )
    _question_block("E. Data Quality & Consistency", requirements["data_quality_questions"], review, "quality", project_id)

    _, right = st.columns([5, 2])
    if right.button("Proceed to Unstructured Data →", type="primary", width="stretch"):
        st.session_state.data_view = "unstructured"
        st.rerun()


def _render_unstructured(project_id, requirements, review):
    _hierarchy(requirements["unstructured_data"], "sources")
    sources = []
    for group in requirements["unstructured_data"]:
        for category in group.get("categories", []):
            for source in category.get("sources", []):
                sources.append((group["group"], category.get("name", "General"), source))

    with st.container(border=True):
        st.caption("For each source, select the trustworthiness classification that best describes how it was generated and verified.")
        header = st.columns([4.5, 3, 2.5])
        header[0].markdown("**Data Source**")
        header[1].markdown("**Category**")
        header[2].markdown("**Trustworthiness**")
        trusts = review.setdefault("trustworthiness", {})
        for group_name, category_name, source in sources:
            source_id = f"{group_name}|{category_name}|{source}"
            saved = trusts.get(source_id, "— Select —")
            row = st.columns([4.5, 3, 2.5])
            row[0].markdown(f"**{source}**")
            row[1].markdown(category_name)
            trust = row[2].selectbox("Trustworthiness", TRUST_OPTIONS, index=TRUST_OPTIONS.index(saved) if saved in TRUST_OPTIONS else 0, label_visibility="collapsed", key=f"trust_{_key(project_id, source_id)}")
            trusts[source_id] = trust

    with st.container(border=True):
        _add_upload_panel(project_id, requirements, structured=False)

    with st.container(border=True):
        st.markdown("### D. Topic Coverage Check")
        st.caption("Data should cover all relevant topics. Gaps in topic coverage can bias the model.")
        topics = review.setdefault("topics", {})
        covered = 0
        columns = st.columns(4)
        for index, topic in enumerate(requirements["topic_coverage"]):
            status = topics.get(topic, "Not Covered")
            if status == "Well Covered":
                covered += 1
            label = f"{topic} · {status}"
            if columns[index % 4].button(label, key=f"topic_{_key(project_id, topic)}", width="stretch"):
                topics[topic] = {"Not Covered": "Partially Covered", "Partially Covered": "Well Covered", "Well Covered": "Not Covered"}[status]
                save_data_review(project_id, review)
                st.rerun()
        st.caption(f"{covered}/{len(requirements['topic_coverage'])} topics adequately covered")

    left, right = st.columns([2, 5])
    if left.button("← Back", width="stretch"):
        st.session_state.data_view = "structured"
        st.rerun()
    if right.button("Proceed to Infrastructure Tab →", type="primary", width="stretch"):
        save_data_review(project_id, review)
        st.switch_page("pages/9_PE_Infrastructure.py")


st.markdown("""
<style>
.dr-card {background:#fff;border:1px solid #d9e2f0;border-radius:10px;padding:24px;margin:12px 0 28px}
.dr-card h3{margin:0 0 24px}.dr-group-label{display:inline-block;border:1px solid;border-radius:7px;padding:8px 16px;font-weight:700;font-size:1rem;margin:8px 0}
.dr-tree{border-left:3px solid;margin:0 0 18px 18px;padding:0 0 0 18px}.dr-category{color:#627695;font-weight:700;margin:8px 0}.dr-chips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px 20px}.dr-chip{background:#fff;border:1px solid #d9e2f0;border-radius:7px;padding:5px 12px;color:#3f4650}.dr-count{text-align:right;color:#8ea2c3;padding-top:10px}.stProgress>div>div>div>div{background:#155eef!important}
div[role="radiogroup"]{gap:5px!important}div[role="radiogroup"] label{border:1px solid #d9e2f0;border-radius:7px;padding:6px 10px;background:#fff}div[role="radiogroup"] label:has(input:checked){border-color:#155eef;background:#eaf1ff}
div[data-testid="stHorizontalBlock"]:has(.dr-data-tab) .stButton>button{background:#fff!important;color:#627695!important;border:0!important;border-radius:0!important;border-bottom:3px solid transparent!important;font-size:1rem!important;white-space:normal!important}
div[data-testid="stHorizontalBlock"]:has(.dr-data-tab-active) [data-testid="column"]:has(.dr-data-tab-active) .stButton>button{color:#155eef!important;border-bottom-color:#155eef!important}
</style>
""", unsafe_allow_html=True)

projects = get_approved_projects()
if not projects:
    st.warning("No governance-approved projects found. Approve a project in Portfolio Gate Review first.")
    st.stop()

project_map = {f"{p['id']} — {p['problem_statement']}": p for p in projects}
selected = st.selectbox("Project", list(project_map), key="data_project")
project = project_map[selected]
project_id = project["id"]

requirements = load_data_requirements(project_id)
if requirements is None:
    with st.spinner("Generating project-specific data requirements…"):
        try:
            requirements = generate_data_requirements(
                project,
                [h for h in load_hypotheses(project_id) if h.get("status") == "Approved"],
                [e for e in load_experiments(project_id) if e.get("status") == "Approved"],
                load_prototype_spec(project_id) or {},
            )
        except Exception:
            requirements = _fallback_requirements()
        requirements = _normalise_requirements(requirements)
        save_data_requirements(project_id, requirements)
else:
    requirements = _normalise_requirements(requirements)

review = load_data_review(project_id) or {}
original_review = copy.deepcopy(review)
st.session_state.setdefault("data_view", "structured")

tab1, tab2, _ = st.columns([2.7, 3, 5])
tab1.markdown(
    f'<span class="dr-data-tab {"dr-data-tab-active" if st.session_state.data_view == "structured" else ""}"></span>',
    unsafe_allow_html=True,
)
if tab1.button("AI Data Readiness: Structured Data", key="structured_tab", width="stretch"):
    st.session_state.data_view = "structured"
    st.rerun()
tab2.markdown(
    f'<span class="dr-data-tab {"dr-data-tab-active" if st.session_state.data_view == "unstructured" else ""}"></span>',
    unsafe_allow_html=True,
)
if tab2.button("AI Data Readiness: Unstructured Data", key="unstructured_tab", width="stretch"):
    st.session_state.data_view = "unstructured"
    st.rerun()

assignments = load_assignments(project_id)
if assignments:
    stakeholders = " · ".join(a["role_key"].replace("_", " ").title() for a in assignments)
    st.caption(f"Stakeholders: {stakeholders}")

if st.session_state.data_view == "structured":
    _render_structured(project_id, requirements, review)
else:
    _render_unstructured(project_id, requirements, review)

if review != original_review:
    save_data_review(project_id, review)
