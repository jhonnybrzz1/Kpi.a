import logging
import os
import traceback
from datetime import datetime

import streamlit as st

from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator
from services.document_extractor import DocumentExtractor
from utils.examples import INITIATIVE_EXAMPLES
from utils.validation import sanitize_text, validate_input

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@st.cache_resource
def get_mistral_service():
    return MistralService()


@st.cache_resource
def get_openai_service():
    return OpenAIService()


@st.cache_resource
def get_pdf_generator():
    return PDFGenerator()


@st.cache_resource
def get_document_extractor():
    return DocumentExtractor()


st.set_page_config(
    page_title="MetricFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/metricflow-ai",
        "Report a bug": "https://github.com/your-repo/metricflow-ai/issues",
        "About": "MetricFlow AI — Sistema Inteligente de Métricas v1.0",
    },
)

st.markdown("""
<style>
/* ── Tipografia base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.mf-header {
    padding: 2.5rem 2rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
    border: 1px solid rgba(99,102,241,.35);
    text-align: center;
    margin-bottom: 2rem;
}
.mf-header h1 {
    margin: 0 0 .4rem;
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -.5px;
}
.mf-header p {
    margin: 0;
    color: #a5b4fc;
    font-size: 1rem;
}
.mf-badge {
    display: inline-block;
    margin-top: .8rem;
    padding: .25rem .75rem;
    border-radius: 999px;
    background: rgba(99,102,241,.25);
    border: 1px solid rgba(99,102,241,.5);
    color: #c7d2fe;
    font-size: .75rem;
    font-weight: 500;
    letter-spacing: .5px;
}

/* ── Sidebar ── */
.mf-step {
    display: flex;
    align-items: flex-start;
    gap: .75rem;
    padding: .75rem 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.mf-step:last-child { border-bottom: none; }
.mf-step-num {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(99,102,241,.2);
    border: 1px solid rgba(99,102,241,.4);
    color: #a5b4fc;
    font-size: .75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.mf-step-body { flex: 1; }
.mf-step-body strong { display: block; color: #e2e8f0; font-size: .85rem; margin-bottom: .15rem; }
.mf-step-body span { color: #94a3b8; font-size: .78rem; }

.mf-stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: .5rem;
    margin-top: .5rem;
}
.mf-stat {
    background: rgba(99,102,241,.1);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 8px;
    padding: .5rem .6rem;
    text-align: center;
}
.mf-stat strong { display: block; color: #a5b4fc; font-size: .95rem; }
.mf-stat span { color: #64748b; font-size: .7rem; }

/* ── Cards de resultado ── */
.mf-card {
    background: rgba(26,26,36,.8);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: .75rem 0;
}
.mf-card-title {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: .25rem;
}
.mf-card-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
}
.mf-card-sub { font-size: .82rem; color: #94a3b8; margin-top: .2rem; }

/* ── Success banner ── */
.mf-success {
    background: linear-gradient(135deg, rgba(16,185,129,.12), rgba(5,150,105,.08));
    border: 1px solid rgba(16,185,129,.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
}
.mf-success h3 { color: #6ee7b7; margin: 0 0 .3rem; font-size: 1.2rem; }
.mf-success p { color: #94a3b8; margin: 0; font-size: .9rem; }

/* ── Error banner ── */
.mf-error {
    background: rgba(239,68,68,.08);
    border: 1px solid rgba(239,68,68,.3);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.mf-error h4 { color: #fca5a5; margin: 0 0 .4rem; }
.mf-error p { color: #94a3b8; margin: 0; font-size: .88rem; }

/* ── Upload info box ── */
.mf-upload-info {
    background: rgba(99,102,241,.08);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 8px;
    padding: .75rem 1rem;
    color: #a5b4fc;
    font-size: .85rem;
    margin-bottom: .75rem;
}

/* ── Footer ── */
.mf-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(255,255,255,.06);
    color: #475569;
    font-size: .82rem;
}
.mf-footer strong { color: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="mf-header">
    <h1>🧠 MetricFlow AI</h1>
    <p>Sistema Inteligente de Métricas Otimizado (metrics-review v2)</p>
    <span class="mf-badge">✦ Mistral AI &nbsp;+&nbsp; OpenAI GPT-5.4 nano</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### Como Funciona")
    steps = [
        ("1", "Descreva a Iniciativa", "Detalhe seu projeto ou funcionalidade"),
        ("2", "Análise Estratégica", "IA define contexto e North Star"),
        ("3", "Hierarchy Review", "Métricas L1/L2 e Health Indicators"),
        ("4", "Actionable OKRs", "Resultados de negócio (Outcomes)"),
    ]
    html_steps = ""
    for num, title, desc in steps:
        html_steps += f"""
        <div class="mf-step">
            <div class="mf-step-num">{num}</div>
            <div class="mf-step-body"><strong>{title}</strong><span>{desc}</span></div>
        </div>"""
    st.markdown(html_steps, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Exemplos de Iniciativas")

    categories = list(set(ex["category"] for ex in INITIATIVE_EXAMPLES.values()))
    selected_category = st.selectbox("Categoria", ["Todas"] + categories, index=0, label_visibility="collapsed")

    filtered = (
        INITIATIVE_EXAMPLES if selected_category == "Todas"
        else {k: v for k, v in INITIATIVE_EXAMPLES.items() if v.get("category") == selected_category}
    )

    for key, example in filtered.items():
        if st.button(example["title"], use_container_width=True, key=f"btn_{key}"):
            st.session_state["example_text"] = example["description"]
            st.rerun()

# ── API Key check ─────────────────────────────────────────────────────────────
def check_api_keys():
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY não configurada")
        return False
    if not os.getenv("MISTRAL_API_KEY"):
        st.error("MISTRAL_API_KEY não configurada")
        return False
    return True

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not check_api_keys():
        st.stop()

    st.markdown("---")

    # ── Input ────────────────────────────────────────────────────────────────
    st.markdown("### Descreva sua Iniciativa")

    default_text = st.session_state.get("example_text", "")
    input_tab, upload_tab = st.tabs(["✏️ Digitar Texto", "📎 Anexar Documento"])

    with input_tab:
        user_input_text = st.text_area(
            "Descrição da iniciativa",
            height=160,
            placeholder="Ex: Quero criar uma funcionalidade de notificação de estoque baixo...",
            value=default_text,
            label_visibility="collapsed",
        )

    with upload_tab:
        uploaded_file = st.file_uploader("Upload", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
        extracted_text = ""
        if uploaded_file:
            extracted_text = get_document_extractor().extract_text(uploaded_file.read(), uploaded_file.name)

    user_input = user_input_text.strip()
    if extracted_text:
        user_input = f"{user_input}\n\n{extracted_text}" if user_input else extracted_text

    # Campos opcionais
    st.markdown("### Informações Adicionais")
    col1, col2 = st.columns(2)
    responsible = col1.text_input("Responsável")
    company = col2.text_input("Empresa")

    if st.button("🚀 Gerar Análise MetricFlow", type="primary", use_container_width=True):
        if not user_input:
            st.warning("Por favor, descreva a iniciativa.")
            return

        try:
            progress = st.progress(0)
            status = st.empty()

            status.caption("🧠 Etapa 1/4 — Contexto (Mistral AI)...")
            progress.progress(25)
            context = get_mistral_service().analyze_context(user_input)

            status.caption("📊 Etapa 2/4 — Arquitetura de Métricas (GPT-5.4 nano)...")
            progress.progress(50)
            metrics = get_openai_service().generate_metrics(user_input, context)

            status.caption("📄 Etapa 3/4 — Relatório...")
            progress.progress(90)
            report_data = {
                "initiative_description": user_input,
                "responsible": responsible or "N/A",
                "company": company or "N/A",
                "date": datetime.now().strftime("%d/%m/%Y"),
                "context_analysis": context,
                "metrics_analysis": metrics,
            }
            pdf_bytes = get_pdf_generator().generate_report(report_data)
            progress.progress(100)
            status.empty()
            st.balloons()

            # ── Resultados ──
            st.markdown("## Análise Estratégica de Métricas")

            # 1. Contexto
            with st.expander("🧠 Contexto e Valor Entregue", expanded=True):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Tipo", context.get("tipo", "N/A"))
                m2.metric("Game", context.get("business_game", "N/A"))
                m3.metric("Objetivo", context.get("objetivo", "N/A"))
                m4.metric("Etapa AARRR", context.get("etapa_funil", "N/A"))
                st.success(f"📝 **Resumo do PRD (Objetivo):** {context.get('resumo_prd', 'N/A')}")
                with st.expander("📊 Dados Identificados", expanded=True):
                    data = context.get('dados_atuais', {})
                    if isinstance(data, str):
                        try: import json; data = json.loads(data)
                        except: st.write(data)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            label = k.replace("_", " ").title()
                            st.write(f"**{label}:** {v}")

            # 2. North Star
            with st.expander("🎯 North Star Metric", expanded=True):
                ns = metrics.get("north_star", {})
                st.markdown(f"### {ns.get('nome', 'N/A')}")
                st.write(ns.get("justificativa", ""))
                st.code(f"Fórmula: {ns.get('definicao', 'N/A')}", language=None)
                st.write("**Validação SMART:**", ", ".join(ns.get("validacao_smart", [])))

            # 3. Health Indicators (L1)
            with st.expander("📈 L1 Health Indicators (Saúde do Produto)", expanded=True):
                l1_list = metrics.get("l1_health_indicators", [])
                for l1 in l1_list:
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.markdown(f"**{l1.get('pilar')}**")
                    c2.markdown(f"**{l1.get('metrica')}**")
                    c3.caption(f"🎯 Meta: {l1.get('meta_sugerida')}")
                    st.write(f"_{l1.get('por_que_importa')}_")
                    st.markdown("---")

            # 4. Diagnostic (L2)
            with st.expander("🔍 L2 Diagnostic Metrics (Investigação)", expanded=False):
                l2_list = metrics.get("l2_diagnostic_metrics", [])
                for l2 in l2_list:
                    st.write(f"🔗 **Vinculada à L1:** {l2.get('vinculo_l1')}")
                    st.write(f"**Métrica:** {l2.get('metrica')}")
                    st.warning(f"⚠️ **Ação se cair:** {l2.get('acao_se_cair')}")
                    st.markdown("---")

            # 5. OKRs
            with st.expander("🏆 OKRs de Resultado (Outcomes)", expanded=True):
                for okr in metrics.get("okrs", []):
                    st.markdown(f"#### 🎯 {okr.get('objetivo')}")
                    for kr in okr.get("key_results", []):
                        st.write(f"✅ **{kr.get('resultado')}**")
                        st.caption(f"Baseline: {kr.get('baseline')} | Meta: {kr.get('meta')}")
                    st.markdown("---")

            # 6. Proteção
            with st.expander("⚖️ Contra-Métricas (Anti-Fraude)", expanded=False):
                for cm in metrics.get("counter_metrics", []):
                    st.write(f"🛡️ **{cm.get('nome')}**")
                    st.write(f"**Protege contra:** {cm.get('protege_contra')}")
                    st.caption(f"❗ Trade-off: {cm.get('trade_off')}")

            # 7. Implementação
            with st.expander("🛠️ Guia de Implementação", expanded=False):
                imp = metrics.get("implementacao", {})
                st.write("**Ferramentas:**", ", ".join(imp.get("ferramentas", [])))
                st.write("**Visualização:**", imp.get("visualizacao", ""))
                for q in imp.get("queries_exemplo", []):
                    st.code(q, language="sql")

            # Download
            st.download_button("📄 Baixar Relatório PDF", data=pdf_bytes, file_name="MetricFlow_Report.pdf", mime="application/pdf", use_container_width=True)

        except Exception as e:
            st.error(f"Erro no processamento: {str(e)}")
            st.code(traceback.format_exc())

def add_footer():
    st.markdown("""<div class="mf-footer"><strong>MetricFlow AI</strong> — v2.0 (metrics-review optimized)</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    add_footer()
