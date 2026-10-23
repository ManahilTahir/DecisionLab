"""Page 1 — Upload Data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.upload_service import load_file, load_sample, SUPPORTED_EXTENSIONS
from services.profiling_service import profile_dataframe, summary_dict

st.set_page_config(page_title="Upload Data — DecisionLab", page_icon="📁", layout="wide")
init_session()
inject_custom_css()
render_page_header("Upload Data", "Bring your CSV or Excel file — DecisionLab will inspect it automatically.")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

col_up, col_sample = st.columns([3, 2])

with col_up:
    st.markdown("##### Upload your file")
    uploaded = st.file_uploader(
        "Choose a CSV or Excel file",
        type=list(SUPPORTED_EXTENSIONS),
        accept_multiple_files=False,
        help=f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}. Max 50 MB.",
    )
    if uploaded is not None:
        result = load_file(uploaded)
        if not result.success:
            st.error(result.error)
        else:
            st.session_state["df"] = result.df
            st.session_state["file_name"] = result.file_name
            st.session_state["profile"] = profile_dataframe(result.df)
            st.session_state["confirmed_mappings"] = {}
            st.success(f"Loaded **{result.file_name}** — {result.df.shape[0]} rows × {result.df.shape[1]} columns.")
            for w in result.warnings:
                st.warning(w)

with col_sample:
    st.markdown("##### Or explore sample data")
    samples = ["sample_sales.csv", "sample_employees.csv", "sample_services.csv"]
    for s in samples:
        if st.button(s, key=f"sample_{s}", width="stretch"):
            result = load_sample(s, DATA_DIR)
            if result.success:
                st.session_state["df"] = result.df
                st.session_state["file_name"] = result.file_name
                st.session_state["profile"] = profile_dataframe(result.df)
                st.session_state["confirmed_mappings"] = {}
                st.success(f"Loaded sample: {s}")
                st.rerun()
            else:
                st.error(result.error)

st.markdown("---")

df = st.session_state.get("df")
if df is None:
    render_empty_state("No data uploaded yet.", "Upload a file or pick a sample to begin.")
    render_footer()
    st.stop()

profile = st.session_state.get("profile")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", profile.n_rows)
c2.metric("Columns", profile.n_cols)
c3.metric("Missing values", profile.total_missing)
c4.metric("Duplicate rows", profile.duplicate_count)

st.markdown("##### Data preview")
st.dataframe(df.head(15), width="stretch", hide_index=True)

st.markdown("##### Column overview")
col_rows = []
for col in profile.columns:
    col_rows.append({
        "Column": col.name,
        "Type": col.dtype,
        "Inferred meaning": col.inferred_role,
        "Missing": col.missing_count,
        "Unique": col.unique_count,
    })
st.dataframe(pd.DataFrame(col_rows), width="stretch", hide_index=True)

st.info("Next: go to **Understand Data** to confirm column meanings, then **Ask a Question**.")
render_footer()