"""DecisionLab — Universal Business Intelligence & Decision Simulator.

Entry point / Home page. Run with: streamlit run app.py
"""
import streamlit as st

from components import inject_custom_css, render_logo, render_footer, init_session

st.set_page_config(
    page_title="DecisionLab — Business Intelligence & Decision Simulator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
inject_custom_css()

with st.sidebar:
    render_logo(width=220, centered=False)
    st.markdown("---")
    st.caption("Navigate using the pages in the sidebar.")
    if st.session_state.get("df") is not None:
        st.success("Data loaded — ready to analyze.")
        st.caption(f"File: `{st.session_state.get('file_name', '')}`")
    else:
        st.info("No data loaded yet.")

render_logo(width=300, centered=True)

st.markdown(
    """
    <div class="dl-hero">
        <h1>DecisionLab</h1>
        <p class="dl-tagline">Turn Your Business Data into Better Decisions</p>
        <p class="dl-description">
            Upload your data, describe your goal, and let DecisionLab identify relevant
            information, perform analysis, and help you compare possible decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.markdown("#### 🚀 Start")
    if st.button("Start New Analysis", width="stretch", type="primary"):
        st.switch_page("pages/1_📁_Upload_Data.py")
with col2:
    st.markdown("#### 📂 Explore")
    if st.button("Explore Sample Data", width="stretch"):
        st.switch_page("pages/1_📁_Upload_Data.py")

st.markdown("---")
st.markdown("### How it works")

steps = [
    ("1", "Upload Data", "Bring your own CSV or Excel file."),
    ("2", "Understand Data", "DecisionLab profiles columns and suggests meanings."),
    ("3", "Ask a Question", "Describe what you want to know in plain words."),
    ("4", "Analyze", "Get relevant metrics, charts, and insights."),
    ("5", "Simulate", "Compare what-if scenarios and export results."),
]
cols = st.columns(len(steps))
for col, (num, title, desc) in zip(cols, steps):
    col.markdown(
        f'<div class="dl-step-card">'
        f'<div class="dl-step-num">{num}</div>'
        f'<h4>{title}</h4><p>{desc}</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#64748B;'>"
    "Works with retail, services, construction estimation, HR, sales, finance, and more — "
    "no fixed industry required."
    "</p>",
    unsafe_allow_html=True,
)

render_footer()