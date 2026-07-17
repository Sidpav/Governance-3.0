import streamlit as st

from database.human_comment_repository import load_human_comment, save_human_comment


def render_human_comment(project_id, scope, recommendation_key, *, label="Feedback / Comment"):
    """Render and persist a reviewer comment beside an AI recommendation."""
    widget_key = f"human_comment_{project_id}_{scope}_{recommendation_key}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = load_human_comment(
            project_id, scope, recommendation_key
        )

    comment = st.text_area(
        label,
        key=widget_key,
        placeholder="Add human context, agreement, conditions, or an override…",
        height=88,
    )
    if st.button(
        "Save comment",
        key=f"save_{widget_key}",
        use_container_width=True,
    ):
        save_human_comment(project_id, scope, recommendation_key, comment)
        st.success("Comment saved.")
    return comment
