"""Page 2 — Understand Data (profiling + column mapping)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.column_mapping_service import suggest_mappings, role_label, ALL_ROLES
from services.profiling_service import summary_dict

st.set_page_config(page_title="Understand Data — DecisionLab", page_icon="🔍", layout="wide")
init_session()
inject_custom_css()
render_page_header("Understand Data", "Review the inferred column meanings and confirm or correct them.")

df = st.session_state.get("df")
profile = st.session_state.get("profile")
if df is None or profile is None:
    render_empty_state("No data loaded.", "Upload data first from the Upload Data page.")
    render_footer()
    st.stop()

st.markdown("##### Dataset summary")
sumd = summary_dict(profile)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", sumd["Rows"])
c2.metric("Columns", sumd["Columns"])
c3.metric("Numerical", sumd["Numerical columns"])
c4.metric("Categorical", sumd["Categorical columns"])

st.markdown("---")
st.markdown("##### Column mapping")
st.caption("Confirm the suggested meaning, change it, or ignore a column. These mappings drive the analysis.")

mappings = st.session_state.get("confirmed_mappings") or suggest_mappings(profile)

col_cols = ["Column", "Sample values", "Suggested meaning", "Confirmed meaning", "Action"]
edited = {}
for col in profile.columns:
    sample = ", ".join(col.sample_values[:3])
    current = mappings.get(col.name, col.inferred_role)
    with st.container():
        mc1, mc2, mc3 = st.columns([2, 2, 2])
        mc1.markdown(f"**{col.name}**\n\n`{col.dtype}` · {col.unique_count} unique")
        mc2.caption(f"e.g. {sample}" if sample else "—")
        new_role = mc3.selectbox(
            "Meaning", ALL_ROLES, index=ALL_ROLES.index(current),
            key=f"role_{col.name}", label_visibility="collapsed"
        )
        edited[col.name] = new_role

st.session_state["confirmed_mappings"] = edited

st.markdown("---")
st.markdown("##### Confirmed mappings")
map_df = pd.DataFrame([
    {"Column": k, "Meaning": role_label(v)} for k, v in edited.items()
])
st.dataframe(map_df, width="stretch", hide_index=True)

st.info("Next: go to **Ask a Question** to describe what you want to know.")
render_footer()