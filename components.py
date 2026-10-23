"""Shared UI components for DecisionLab: logo, footer, and base styling."""
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).parent
STATIC = ROOT / "static"


def inject_custom_css():
    css_path = STATIC / "css" / "custom.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_logo(width: int = 300, centered: bool = True):
    logo_path = STATIC / "logo.svg"
    if not logo_path.exists():
        st.title("DecisionLab")
        return
    svg = logo_path.read_text(encoding="utf-8")
    align = "center" if centered else "left"
    st.markdown(
        f'<div class="dl-logo" style="text-align:{align};">'
        f'<img src="data:image/svg+xml;base64,{_b64(svg)}" width="{width}"/>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="dl-page-header">'
        f'<h2>{title}</h2>'
        f'<p class="dl-subtitle">{subtitle}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        '<div class="dl-footer">'
        '<span class="dl-footer-divider"></span>'
        '<span class="dl-footer-text">Developed by: <strong>Manahil Tahir</strong></span>'
        '<span class="dl-footer-divider"></span>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_empty_state(message: str, hint: str = ""):
    body = f"<p>{message}</p>"
    if hint:
        body += f"<p class='dl-empty-hint'>{hint}</p>"
    st.markdown(f'<div class="dl-empty-state">{body}</div>', unsafe_allow_html=True)


def _b64(text: str) -> str:
    import base64
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def init_session():
    defaults = {
        "df": None,
        "file_name": None,
        "profile": None,
        "column_mappings": {},
        "confirmed_mappings": {},
        "current_question": None,
        "question_interpretation": None,
        "analysis_result": None,
        "scenarios": [],
        "processed_df": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value