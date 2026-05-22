import streamlit as st


def render_header() -> None:
    st.markdown(
        """
<div class="mf-header">
    <h1>🧠 MetricFlow AI</h1>
    <p>Sistema Inteligente de Arquitetura de Métricas Estratégicas</p>
    <span class="mf-badge">✦ Powered by Mistral AI + OpenRouter Gemma 4</span>
</div>
""",
        unsafe_allow_html=True,
    )
