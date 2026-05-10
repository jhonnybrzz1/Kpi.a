import streamlit as st


def render_footer() -> None:
    text = "<strong>MetricFlow AI</strong> — v2.0 (metrics-review optimized)"
    st.markdown(
        f'<div class="mf-footer">{text}</div>',
        unsafe_allow_html=True,
    )
