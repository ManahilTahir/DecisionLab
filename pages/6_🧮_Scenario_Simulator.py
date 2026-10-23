"""Page 5 — Scenario Simulator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components import inject_custom_css, render_page_header, render_footer, render_empty_state, init_session
from services.column_mapping_service import columns_by_role, role_label
from services.scenario_engine import run_financial_scenario, scenario_to_df
from services.report_service import df_to_csv_bytes, safe_filename

st.set_page_config(page_title="Scenario Simulator — DecisionLab", page_icon="🧮", layout="wide")
init_session()
inject_custom_css()
render_page_header("Scenario Simulator", "Compare what-if scenarios. Results are estimates, not guarantees.")

df = st.session_state.get("df")
mappings = st.session_state.get("confirmed_mappings") or {}
if df is None:
    render_empty_state("No data loaded.", "Upload data first.")
    render_footer()
    st.stop()

rev_cols = columns_by_role(mappings, "revenue")
cost_cols = columns_by_role(mappings, "expense")
if not rev_cols and not cost_cols:
    render_empty_state("No revenue or expense columns confirmed.", "Confirm column meanings in Understand Data.")
    render_footer()
    st.stop()

import pandas as pd
baseline_rev = float(pd.to_numeric(df[rev_cols[0]], errors="coerce").sum()) if rev_cols else 0.0
baseline_cost = float(pd.to_numeric(df[cost_cols[0]], errors="coerce").sum()) if cost_cols else 0.0

c1, c2 = st.columns(2)
with c1:
    st.metric("Baseline Revenue", f"{baseline_rev:,.2f}")
with c2:
    st.metric("Baseline Cost", f"{baseline_cost:,.2f}")

st.markdown("---")
st.markdown("##### Scenario controls")
name = st.text_input("Scenario name", value="Scenario 1")
price_change = st.slider("Price change (%)", -50, 50, 0) / 100
volume_change = st.slider("Volume change (%)", -50, 50, 0) / 100
cost_change = st.slider("Cost change (%)", -50, 50, 0) / 100

if st.button("Run scenario", type="primary", width="stretch"):
    res = run_financial_scenario(name, baseline_rev, baseline_cost, price_change, volume_change, cost_change)
    st.session_state["scenarios"].append(res)

    st.markdown("##### Results")
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Projected Revenue", f"{res.projected_revenue:,.2f}", f"{res.revenue_delta:,.2f}")
    cm2.metric("Projected Cost", f"{res.projected_cost:,.2f}", f"{res.cost_delta:,.2f}")
    cm3.metric("Projected Profit", f"{res.projected_profit:,.2f}", f"{res.profit_delta:,.2f}")

    st.dataframe(scenario_to_df(res), width="stretch", hide_index=True)
    for note in res.notes:
        st.caption(note)

    st.download_button("Download scenario (CSV)", df_to_csv_bytes(scenario_to_df(res)),
                       file_name=f"{safe_filename(name)}_scenario.csv", mime="text/csv")

render_footer()