"""Page 7 — Saved Projects."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from database.database import get_connection, save_project, list_projects, list_scenarios

st.set_page_config(page_title="Saved Projects — DecisionLab", page_icon="💾", layout="wide")
init_session()
inject_custom_css()
render_page_header("Saved Projects", "Persistent project configurations and scenarios (SQLite).")

conn = get_connection()

st.markdown("##### Save current session as a project")
with st.form("save_project_form"):
    pname = st.text_input("Project name", value="")
    fname = st.session_state.get("file_name", "")
    submitted = st.form_submit_button("Save project", type="primary")
    if submitted and pname:
        pid = save_project(pname, fname, conn)
        st.success(f"Saved project '{pname}' (ID {pid}).")

st.markdown("---")
st.markdown("##### Saved projects")
projects = list_projects(conn)
if projects:
    st.dataframe(pd.DataFrame(projects), width="stretch", hide_index=True)
else:
    st.info("No saved projects yet.")

st.markdown("##### Saved scenarios")
scenarios = list_scenarios(conn)
if scenarios:
    scen_df = pd.DataFrame(scenarios)[["id", "name", "created_at"]]
    st.dataframe(scen_df, width="stretch", hide_index=True)
else:
    st.info("No saved scenarios yet.")

render_footer()