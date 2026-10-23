"""Page 4 — Analysis Workspace."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.column_mapping_service import columns_by_role, role_label
from services.analytics_engine import (
    group_aggregate, percentage_contribution, trend_over_time,
    correlation_matrix, describe_numeric, AnalysisResult,
)
from services.insight_engine import generate_insights
from services.visualization_service import bar_chart, line_chart, pie_chart, heatmap
from services.report_service import df_to_csv_bytes, build_summary_report, safe_filename

st.set_page_config(page_title="Analysis Workspace — DecisionLab", page_icon="📊", layout="wide")
init_session()
inject_custom_css()
render_page_header("Analysis Workspace", "Results, charts, and insights for your question.")

df = st.session_state.get("df")
mappings = st.session_state.get("confirmed_mappings") or {}
question = st.session_state.get("current_question", "")
interp = st.session_state.get("question_interpretation")

if df is None:
    render_empty_state("No data loaded.", "Upload data first.")
    render_footer()
    st.stop()

if not question or interp is None:
    render_empty_state("No question interpreted yet.", "Go to Ask a Question and click Interpret.")
    render_footer()
    st.stop()

st.markdown(f"**Question:** {question}")
st.markdown(
    f"Metric: `{role_label(interp.metric_role)}` · Group: `{role_label(interp.group_role)}` · "
    f"Operation: `{interp.operation}` · Confidence: `{interp.confidence}`"
)
st.markdown("---")

metric_cols = columns_by_role(mappings, interp.metric_role) if interp.metric_role else []
group_cols = columns_by_role(mappings, interp.group_role) if interp.group_role else []

if not metric_cols and interp.operation not in ("summary", "what_if"):
    st.warning("No matching metric column found. Confirm column meanings in Understand Data.")
    render_footer()
    st.stop()

metric_col = metric_cols[0] if metric_cols else ""
group_col = group_cols[0] if group_cols else ""

result = AnalysisResult(question=question, metric_col=metric_col, group_col=group_col, operation=interp.operation)

if interp.operation in ("highest", "lowest", "summary") and metric_col and group_col:
    grouped = group_aggregate(df, group_col, metric_col, "sum")
    result.grouped = grouped
    result.summary["total"] = float(grouped[metric_col].sum())
    result.summary["top_group"] = str(grouped.iloc[0][group_col])
    result.summary["top_value"] = float(grouped.iloc[0][metric_col])

    st.markdown("##### Ranked results")
    contrib = percentage_contribution(grouped, metric_col)
    st.dataframe(contrib, width="stretch", hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(bar_chart(grouped, group_col, metric_col,
                            title=f"{role_label(interp.metric_role)} by {role_label(interp.group_role)}"))
    with c2:
        st.pyplot(pie_chart(contrib, group_col, metric_col,
                            title=f"{role_label(interp.metric_role)} contribution"))

elif interp.operation == "trend" and metric_col:
    date_cols = st.session_state["profile"].datetime_columns
    date_col = date_cols[0] if date_cols else ""
    if date_col:
        trend = trend_over_time(df, date_col, metric_col)
        result.trend = trend
        st.markdown("##### Trend over time")
        st.dataframe(trend, width="stretch", hide_index=True)
        st.pyplot(line_chart(trend, date_col, metric_col, title=f"{role_label(interp.metric_role)} trend"))
    else:
        st.warning("No date column detected for trend analysis.")

elif interp.operation == "summary":
    st.markdown("##### Dataset overview")
    num_cols = st.session_state["profile"].numerical_columns
    for nc in num_cols[:6]:
        stats = describe_numeric(df[nc])
        if stats:
            st.markdown(f"**{nc}**")
            st.dataframe(pd.DataFrame([stats]), width="stretch", hide_index=True)
    if len(num_cols) >= 2:
        corr = correlation_matrix(df)
        result.correlations = corr
        st.pyplot(heatmap(corr))

result.insights = generate_insights(df, mappings)
st.markdown("---")
st.markdown("##### Automatic insights")
for ins in result.insights:
    st.markdown(f"- {ins}")

st.session_state["analysis_result"] = result

st.markdown("---")
st.markdown("##### Export")
cexp1, cexp2 = st.columns(2)
with cexp1:
    if result.grouped is not None:
        st.download_button("Download results (CSV)", df_to_csv_bytes(result.grouped),
                           file_name=f"{safe_filename(question)}_results.csv", mime="text/csv")
with cexp2:
    report = build_summary_report(question, mappings, result.summary, result.insights)
    st.download_button("Download summary report (CSV)", df_to_csv_bytes(report),
                       file_name=f"{safe_filename(question)}_report.csv", mime="text/csv")

render_footer()