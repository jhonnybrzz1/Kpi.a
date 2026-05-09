import streamlit as st


def render_footer() -> None:
    st.markdown(
        '<div class="mf-footer"><strong>MetricFlow AI</strong> — v2.0 (metrics-review optimized)</div>',
        unsafe_allow_html=True,
    )
