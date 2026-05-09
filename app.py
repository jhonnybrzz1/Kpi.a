import logging
import os
import traceback
from datetime import datetime
from typing import Any, Dict

import streamlit as st

from config import load_prompts
from services.document_extractor import DocumentExtractor
from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator
from ui.footer import render_footer
from ui.header import render_header
from ui.results import render_results
from ui.sidebar import render_sidebar
from ui.styles import inject_styles
from utils.cache_key import build_cache_key, normalize_input
from utils.security import (
    MAX_ANALYSES_PER_SESSION,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    redact_log_message,
    security_choke_point,
)
from utils.validation import check_api_keys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_IS_PRODUCTION = os.getenv("ENV", "production") == "production"


@st.cache_resource
def get_mistral_service() -> MistralService:
    return MistralService()


@st.cache_resource
def get_openai_service() -> OpenAIService:
    return OpenAIService()


@st.cache_resource
def get_pdf_generator() -> PDFGenerator:
    return PDFGenerator()


@st.cache_resource
def get_document_extractor() -> DocumentExtractor:
    return DocumentExtractor()


def _prompts_raw() -> str:
    config_path = os.path.join(os.path.dirname(__file__), "config", "prompts.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return f.read()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_analyze_context(initiative_text: str, _cache_key: str) -> Dict[str, Any]:
    logger.info("cache miss: analyze_context key=%s", _cache_key)
    return get_mistral_service().analyze_context(initiative_text)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_generate_metrics(
    initiative_text: str, context_json: str, _cache_key: str
) -> Dict[str, Any]:
    import json
    logger.info("cache miss: generate_metrics key=%s", _cache_key)
    return get_openai_service().generate_metrics(initiative_text, json.loads(context_json))


def _init_session_metrics() -> None:
    defaults = {
        "analysis_count": 0,
        "core_called_total": 0,
        "core_blocked_prompt_injection_total": 0,
        "core_blocked_rate_limit_total": 0,
        "upload_rejected_total": 0,
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)


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

inject_styles()
render_header()
render_sidebar()


def main() -> None:
    _init_session_metrics()

    if not check_api_keys():
        st.stop()

    # ── DEV: reload de prompts ────────────────────────────────────────────────
    if not _IS_PRODUCTION:
        with st.sidebar:
            st.markdown("---")
            if st.button("🔄 Reload prompts", help="Invalida cache de prompts e de resultados"):
                load_prompts.cache_clear()
                cached_analyze_context.clear()
                cached_generate_metrics.clear()
                st.success("Prompts recarregados e cache invalidado.")

    st.markdown("---")
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
        uploaded_file = st.file_uploader(
            "Upload", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed"
        )
        extracted_text = ""
        if uploaded_file:
            # ── Upload size guard (before any processing) ─────────────────────
            if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                st.session_state["upload_rejected_total"] += 1
                st.error(
                    f"Arquivo muito grande ({uploaded_file.size // (1024*1024):.1f} MB). "
                    f"Limite: {MAX_FILE_SIZE_MB} MB."
                )
                uploaded_file = None
            else:
                extracted_text = get_document_extractor().extract_text(
                    uploaded_file.read(), uploaded_file.name
                )

    user_input = user_input_text.strip()
    if extracted_text:
        user_input = f"{user_input}\n\n{extracted_text}" if user_input else extracted_text

    st.markdown("### Informações Adicionais")
    col1, col2 = st.columns(2)
    responsible = col1.text_input("Responsável")
    company = col2.text_input("Empresa")

    if st.button("🚀 Gerar Análise MetricFlow", type="primary", use_container_width=True):
        if not user_input:
            st.warning("Por favor, descreva a iniciativa.")
            return

        # ── Rate limit guard (before AI) ──────────────────────────────────────
        if st.session_state["analysis_count"] >= MAX_ANALYSES_PER_SESSION:
            st.session_state["core_blocked_rate_limit_total"] += 1
            st.error(
                f"Limite de {MAX_ANALYSES_PER_SESSION} análises por sessão atingido. "
                "Recarregue a página para iniciar uma nova sessão."
            )
            return

        # ── Security choke point (before AI) ─────────────────────────────────
        check = security_choke_point(user_input)
        if not check["ok"]:
            if check["reason"] == "prompt_injection":
                st.session_state["core_blocked_prompt_injection_total"] += 1
            logger.warning(
                "security_choke_point blocked: reason=%s", check["reason"]
            )
            st.error(check["message_user"])
            return

        safe_input = check["sanitized_prompt"]

        # ── AI pipeline ───────────────────────────────────────────────────────
        st.session_state["core_called_total"] += 1
        st.session_state["analysis_count"] += 1

        try:
            import json

            prompts_raw = _prompts_raw()
            mistral_params = {"model": "mistral-large-2512", "temperature": 0.3, "max_tokens": 2000}
            openai_params = {"model": "gpt-5.4-nano", "temperature": 0.4, "max_completion_tokens": 8000}

            key_stage1 = build_cache_key(safe_input, mistral_params["model"], prompts_raw, mistral_params)
            key_stage2_base = build_cache_key(safe_input, openai_params["model"], prompts_raw, openai_params)

            with st.status("🧠 Etapa 1/4 — Contexto (Mistral AI)...", expanded=False) as s:
                context = cached_analyze_context(normalize_input(safe_input), key_stage1)
                s.update(label="✅ Contexto analisado", state="complete")

            with st.status("📊 Etapa 2/4 — Arquitetura de Métricas...", expanded=False) as s:
                context_json = json.dumps(context, ensure_ascii=False)
                key_stage2 = f"{key_stage2_base}:{hash(context_json)}"
                metrics = cached_generate_metrics(normalize_input(safe_input), context_json, key_stage2)
                s.update(label="✅ Métricas geradas", state="complete")

            with st.status("✍️ Etapa 3/4 — Resumo Executivo...", expanded=False) as s:
                executive_summary = ""
                try:
                    executive_summary = get_openai_service().generate_executive_summary(
                        safe_input, context, metrics
                    )
                except Exception as summary_err:
                    logger.warning("Resumo executivo não gerado: %s", redact_log_message(str(summary_err)))
                s.update(label="✅ Resumo gerado", state="complete")

            with st.status("📄 Etapa 4/4 — Relatório PDF...", expanded=False) as s:
                report_data = {
                    "initiative_description": safe_input,
                    "responsible": responsible or "N/A",
                    "company": company or "N/A",
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "context_analysis": context,
                    "metrics_analysis": metrics,
                    "executive_summary": executive_summary,
                }
                pdf_bytes = get_pdf_generator().generate_report(report_data)
                s.update(label="✅ Relatório pronto", state="complete")

            st.balloons()
            render_results(context, metrics, pdf_bytes)

        except Exception as e:
            logger.error("pipeline error: %s", redact_log_message(str(e)))
            st.error("Ocorreu um erro no processamento. Tente novamente.")
            if not _IS_PRODUCTION:
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
    render_footer()
