import streamlit as st


def render_header() -> None:
    st.markdown(
        """
<div class="mf-header">
    <h1>🧠 MetricFlow AI</h1>
    <p>Sistema Inteligente de Métricas Otimizado (metrics-review v2)</p>
    <span class="mf-badge">✦ Mistral AI &nbsp;+&nbsp; OpenAI GPT-5.4 nano</span>
</div>
""",
        unsafe_allow_html=True,
    )
