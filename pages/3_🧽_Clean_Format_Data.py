"""Page 8 — Clean & Format Data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.cleaning_service import (
    remove_duplicates, handle_nulls, format_dates, convert_type,
    standardize_text, null_summary, DATE_FORMATS,
)

st.set_page_config(page_title="Clean & Format — DecisionLab", page_icon="🧽", layout="wide")
init_session()
inject_custom_css()
render_page_header("Clean & Format Data", "Remove duplicates, handle missing values, and format columns — especially dates. Original upload is never modified.")

df = st.session_state.get("df")
if df is None:
    render_empty_state("No data loaded.", "Upload data first from the Upload Data page.")
    render_footer()
    st.stop()

cleaned = st.session_state.get("cleaned_df")
if cleaned is None:
    cleaned = df.copy()
    st.session_state["cleaned_df"] = cleaned

c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(cleaned))
c2.metric("Columns", len(cleaned.columns))
c3.metric("Duplicates", int(cleaned.duplicated().sum()))

st.markdown("---")

tab_dup, tab_null, tab_date, tab_type, tab_text = st.tabs([
    "🗑️ Duplicates", "📭 Null Values", "📅 Date Format", "🔁 Type Conversion", "🔤 Text",
])

with tab_dup:
    st.markdown("##### Remove duplicate rows")
    st.caption(f"Current duplicate count: **{int(cleaned.duplicated().sum())}**")
    if st.button("Remove all duplicates", width="stretch", type="primary"):
        res = remove_duplicates(cleaned)
        st.session_state["cleaned_df"] = res.df
        st.success(res.message)
        st.rerun()

with tab_null:
    st.markdown("##### Handle missing values")
    ns = null_summary(cleaned)
    if ns.empty:
        st.success("No missing values found in any column.")
    else:
        st.dataframe(ns, width="stretch", hide_index=True)
        null_cols = ns["Column"].tolist()
        col = st.selectbox("Column to clean", null_cols)
        strategy = st.selectbox("Strategy", ["drop", "mean", "median", "mode", "custom"],
                                help="drop=remove rows, mean/median=numeric fill, mode=most frequent, custom=your value")
        fill_val = ""
        if strategy == "custom":
            fill_val = st.text_input("Fill value")
        if st.button("Apply", width="stretch", type="primary"):
            res = handle_nulls(cleaned, col, strategy, fill_val)
            if res.changed:
                st.session_state["cleaned_df"] = res.df
                st.success(res.message)
                st.rerun()
            else:
                st.info(res.message)

with tab_date:
    st.markdown("##### Format date columns")
    st.caption("Parse mixed date formats (e.g. 5/2/2010, 19/02/2010) and convert to a single consistent format.")
    all_cols = cleaned.columns.tolist()
    date_col = st.selectbox("Date column", all_cols, index=0)
    target_label = st.selectbox("Target format", list(DATE_FORMATS.keys()))
    sample = cleaned[date_col].dropna().head(5).tolist()
    st.caption(f"Sample values: {sample}")
    if st.button("Format dates", width="stretch", type="primary"):
        res = format_dates(cleaned, date_col, DATE_FORMATS[target_label])
        if res.changed:
            st.session_state["cleaned_df"] = res.df
            st.success(res.message)
            st.rerun()
        else:
            st.error(res.message)

with tab_type:
    st.markdown("##### Convert column data type")
    tc = st.selectbox("Column", all_cols)
    tt = st.selectbox("Convert to", ["numeric", "text", "datetime"])
    st.caption(f"Current type: `{cleaned[tc].dtype}`")
    if st.button("Convert", width="stretch", type="primary"):
        res = convert_type(cleaned, tc, tt)
        if res.changed:
            st.session_state["cleaned_df"] = res.df
            st.success(res.message)
            st.rerun()
        else:
            st.error(res.message)

with tab_text:
    st.markdown("##### Standardize text columns")
    tx_col = st.selectbox("Text column", all_cols)
    strip = st.checkbox("Trim whitespace", value=True)
    title_case = st.checkbox("Title Case", value=False)
    if st.button("Standardize", width="stretch", type="primary"):
        res = standardize_text(cleaned, tx_col, strip, title_case)
        if res.changed:
            st.session_state["cleaned_df"] = res.df
            st.success(res.message)
            st.rerun()
        else:
            st.error(res.message)

st.markdown("---")
st.markdown("##### Cleaned data preview")
st.dataframe(cleaned.head(15), width="stretch", hide_index=True)

st.markdown("##### Before / After summary")
ba1, ba2 = st.columns(2)
with ba1:
    st.caption("Original")
    st.metric("Rows", len(df), delta=len(cleaned) - len(df))
    st.metric("Missing values", int(df.isna().sum().sum()))
with ba2:
    st.caption("Cleaned")
    st.metric("Rows", len(cleaned))
    st.metric("Missing values", int(cleaned.isna().sum().sum()))

st.markdown("---")
cexp1, cexp2 = st.columns(2)
with cexp1:
    st.download_button("Download cleaned data (CSV)", cleaned.to_csv(index=False).encode("utf-8"),
                       file_name="cleaned_data.csv", mime="text/csv")
with cexp2:
    if st.button("Reset to original", width="stretch"):
        st.session_state["cleaned_df"] = df.copy()
        st.rerun()

render_footer()