"""Page 6 — Data Quality."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.analytics_engine import detect_outliers

st.set_page_config(page_title="Data Quality — DecisionLab", page_icon="🧹", layout="wide")
init_session()
inject_custom_css()
render_page_header("Data Quality", "Inspect and clean your data. The original upload is never modified silently.")

df = st.session_state.get("df")
profile = st.session_state.get("profile")
if df is None or profile is None:
    render_empty_state("No data loaded.", "Upload data first.")
    render_footer()
    st.stop()

processed = st.session_state.get("processed_df")
if processed is None:
    processed = df.copy()

c1, c2, c3 = st.columns(3)
c1.metric("Missing values", profile.total_missing)
c2.metric("Duplicate rows", profile.duplicate_count)
c3.metric("Columns", profile.n_cols)

st.markdown("---")
st.markdown("##### Missing values by column")
miss_rows = [{"Column": col.name, "Missing": col.missing_count, "%": col.missing_pct}
             for col in profile.columns if col.missing_count > 0]
if miss_rows:
    st.dataframe(pd.DataFrame(miss_rows), width="stretch", hide_index=True)
else:
    st.success("No missing values detected.")

st.markdown("##### Potential outliers (IQR method)")
num_cols = profile.numerical_columns
out_cols = st.columns(2)
for i, nc in enumerate(num_cols[:6]):
    with out_cols[i % 2]:
        outliers = detect_outliers(df[nc])
        count = int(outliers.sum())
        st.metric(f"{nc}", f"{count} outliers")

st.markdown("---")
st.markdown("##### Cleaning actions")
col1, col2 = st.columns(2)
with col1:
    if st.button("Remove duplicate rows", width="stretch"):
        before = len(processed)
        processed = processed.drop_duplicates()
        st.success(f"Removed {before - len(processed)} duplicates. {len(processed)} rows remain.")
with col2:
    if st.button("Fill numeric missing with median", width="stretch"):
        for nc in num_cols:
            med = pd.to_numeric(processed[nc], errors="coerce").median()
            processed[nc] = pd.to_numeric(processed[nc], errors="coerce").fillna(med)
        st.success("Filled numeric missing values with column medians.")

st.session_state["processed_df"] = processed

st.markdown("---")
st.markdown("##### Cleaned data preview")
st.dataframe(processed.head(15), width="stretch", hide_index=True)
st.caption(f"Cleaned: {len(processed)} rows × {len(processed.columns)} columns (original: {len(df)} rows).")

render_footer()