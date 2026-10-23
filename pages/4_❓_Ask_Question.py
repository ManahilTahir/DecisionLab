"""Page 3 — Ask a Business Question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.column_mapping_service import role_label, columns_by_role
from services.question_engine import interpret, SUGGESTED_QUESTIONS, GOAL_BUTTONS, OTHER_QUESTIONS

st.set_page_config(page_title="Ask a Question — DecisionLab", page_icon="❓", layout="wide")
init_session()
inject_custom_css()
render_page_header("Ask a Business Question", "Describe what you want to know — DecisionLab will find the relevant columns.")

df = st.session_state.get("df")
mappings = st.session_state.get("confirmed_mappings") or {}
if df is None:
    render_empty_state("No data loaded.", "Upload data first.")
    render_footer()
    st.stop()

st.markdown("##### What would you like to know about your business data?")
question = st.text_input(
    "Your question", value=st.session_state.get("current_question", ""),
    placeholder="e.g. Which service category generates the highest revenue?",
    label_visibility="collapsed",
)

st.markdown("##### Suggested questions")
sq_cols = st.columns(2)
for i, sq in enumerate(SUGGESTED_QUESTIONS):
    with sq_cols[i % 2]:
        if st.button(sq, key=f"sq_{i}", width="stretch"):
            question = sq
            st.session_state["current_question"] = sq
            st.rerun()

st.markdown("##### Or pick a goal")
gb_cols = st.columns(3)
for i, (label, role) in enumerate(GOAL_BUTTONS):
    with gb_cols[i % 3]:
        if st.button(label, key=f"goal_{i}", width="stretch"):
            if role == "what_if":
                question = "What happens if I reduce costs by 10%?"
            elif role == "summary":
                question = "Analyze this dataset and summarize the most important findings."
            else:
                avail = columns_by_role(mappings, role)
                metric = "revenue" if columns_by_role(mappings, "revenue") else "performance"
                if avail:
                    question = f"Which {role_label(role)} has the highest {role_label(metric)}?"
                else:
                    question = f"Analyze {role_label(role)} performance."
            st.session_state["current_question"] = question
            st.rerun()

st.markdown("---")
with st.expander("💬 Other Questions — Ask anything about your data", expanded=False):
    st.caption("Type your own question or pick from these general data questions. You can ask about anything related to your uploaded data.")
    custom_q = st.text_area(
        "Your custom question",
        placeholder="e.g. What is the average salary by department? or How many projects were completed in 2024?",
        height=80,
    )
    if st.button("Use this question", key="use_custom", width="stretch"):
        if custom_q.strip():
            question = custom_q.strip()
            st.session_state["current_question"] = question
            st.rerun()
    st.markdown("**More suggested questions:**")
    oq_cols = st.columns(2)
    for i, oq in enumerate(OTHER_QUESTIONS):
        with oq_cols[i % 2]:
            if st.button(oq, key=f"oq_{i}", width="stretch"):
                question = oq
                st.session_state["current_question"] = oq
                st.rerun()

st.markdown("---")
if st.button("Interpret question", type="primary", width="stretch") and question:
    interp = interpret(question, mappings)
    st.session_state["current_question"] = question
    st.session_state["question_interpretation"] = interp

    st.markdown("##### Interpretation")
    ic1, ic2, ic3, ic4 = st.columns(4)
    ic1.metric("Metric", role_label(interp.metric_role) if interp.metric_role else "—")
    ic2.metric("Group by", role_label(interp.group_role) if interp.group_role else "—")
    ic3.metric("Operation", interp.operation)
    ic4.metric("Confidence", interp.confidence)

    if interp.needs_clarification:
        st.warning(interp.clarification)
    else:
        st.success("Interpretation ready. Go to **Analysis Workspace** to see results.")

render_footer()