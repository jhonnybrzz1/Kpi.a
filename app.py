import logging
import os
import traceback
from typing import Any, Dict

import streamlit as st

from config import load_prompts
from services.document_extractor import DocumentExtractor
from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.orchestrator import AnalysisPipeline
from services.pdf_generator import PDFGenerator
from ui.footer import render_footer
from ui.handlers import StreamlitUIHandler
from ui.header import render_header
from ui.results import render_results
from ui.sidebar import render_sidebar
from ui.styles import inject_styles
from utils.cache_key import build_cache_key
from utils.history import save_snapshot
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

_IS_PRODUCTION = os.getenv("STREAMLIT_ENVIRONMENT", "production") == "production"


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

    # ── DEV: reload de prompts + /metrics/ai ─────────────────────────────────
    if not _IS_PRODUCTION:
        with st.sidebar:
            st.markdown("---")
            if st.button("🔄 Reload prompts", help="Invalida cache de prompts e de resultados"):
                load_prompts.cache_clear()
                cached_analyze_context.clear()
                cached_generate_metrics.clear()
                st.success("Prompts recarregados e cache invalidado.")

            st.markdown("---")
            st.markdown("#### 📊 /metrics/ai (últimos 7 dias)")
            if st.button("Atualizar métricas", key="refresh_metrics"):
                st.session_state["_metrics_data"] = None
            from utils.ai_metrics import get_metrics_summary

            if "_metrics_data" not in st.session_state:
                st.session_state["_metrics_data"] = get_metrics_summary(days=7)
            summary = st.session_state["_metrics_data"]
            if not summary["byModel"]:
                st.caption("Nenhuma chamada registrada ainda.")
            else:
                import json as _json

                st.json(_json.dumps(summary, indent=2))

            st.markdown("---")
            st.markdown("#### 📊 Market Benchmark (D7)")
            if st.button("Gerar Research Report", key="generate_benchmark"):
                from utils.benchmarks import generate_report

                path = generate_report()
                st.success(f"Relatório gerado em: `{path}`")
                with st.expander("👁️ Visualizar Relatório", expanded=True):
                    with open(path, "r", encoding="utf-8") as f:
                        st.markdown(f.read())

    st.markdown("---")

    # ── Handle View Switching ────────────────────────────────────────────────
    current_view = st.session_state.get("_view", "main")

    # Check for direct ID access in URL
    query_params = st.query_params
    if "id" in query_params:
        snapshot_id = query_params["id"]
        from utils.history import calculate_content_hash, get_history

        history = get_history()
        match = next((h for h in history if h["snapshot_id"] == snapshot_id), None)

        from utils.telemetry import record_telemetry_event

        if match:
            # Validation: version and content_hash
            is_valid = match.get("version") == "v1"
            if is_valid:
                expected_hash = calculate_content_hash(match["payload"])
                if match.get("content_hash") != expected_hash:
                    is_valid = False
                    st.error(f"Snapshot `{snapshot_id}` corrompido ou alterado localmente.")

            record_telemetry_event(f"analysis_opened_by_id_valid_{str(is_valid).lower()}")

            if is_valid:
                st.session_state["_restore_snapshot"] = match
                st.query_params.clear()
                st.rerun()
        else:
            record_telemetry_event("analysis_opened_by_id_not_found")
            st.error(f"Snapshot com ID `{snapshot_id}` não encontrado.")

    if current_view == "compare":
        from ui.comparison import render_comparison
        from utils.history import get_history

        history = get_history()
        compare_ids = st.session_state.get("compare_ids", [])
        snapshots_to_compare = [h for h in history if h["snapshot_id"] in compare_ids]

        # Validation: check mandatory fields for comparison (Snapshot Contract v1)
        valid = True
        for s in snapshots_to_compare:
            m = s["payload"].get("metrics", {})
            c = s["payload"].get("context", {})
            if not m.get("north_star") or not m.get("okrs") or not c.get("etapa_funil"):
                st.error(f"Snapshot `{s['snapshot_id']}` é inválido para comparação.")
                valid = False

        if valid and len(snapshots_to_compare) == 2:
            render_comparison(snapshots_to_compare)
            return
        else:
            st.session_state["_view"] = "main"
            st.rerun()

    # ── Restore snapshot (sem reanalisar) ─────────────────────────────────────
    restored_item = st.session_state.pop("_restore_snapshot", None)
    if restored_item:
        st.session_state["_was_restored"] = True
        snapshot_id = restored_item["snapshot_id"]
        restored = restored_item["payload"]
        saved_at = (
            restored_item.get("saved_at", "")[:16].replace("T", " ")
            if "saved_at" in restored_item
            else ""
        )
        st.info(
            f"🕘 Exibindo análise salva{f' de {saved_at}' if saved_at else ''} — sem reexecutar.",
            icon="ℹ️",
        )

        # Display inputs as text or readonly equivalents to show what was used
        st.markdown(f"**Iniciativa:**\n{restored.get('initiative_text', '')}")
        col1, col2 = st.columns(2)
        col1.markdown(f"**Responsável:** {restored.get('responsible', '')}")
        col2.markdown(f"**Empresa:** {restored.get('company', '')}")

        render_results(
            restored["context"],
            restored["metrics"],
            restored["pdf_bytes"],
            restored["artifact_result"],
            snapshot_id=snapshot_id,
        )
        return

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
                    f"Arquivo muito grande ({uploaded_file.size // (1024 * 1024):.1f} MB). "
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
        if st.session_state.get("_was_restored", False):
            from utils.telemetry import record_telemetry_event

            record_telemetry_event("generation_started_after_reload")
            st.session_state["_was_restored"] = False

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
            logger.warning("security_choke_point blocked: reason=%s", check["reason"])
            st.error(check["message_user"])
            return

        safe_input = check["sanitized_prompt"]

        # ── AI pipeline ───────────────────────────────────────────────────────
        st.session_state["core_called_total"] += 1
        st.session_state["analysis_count"] += 1

        try:
            prompts_raw = _prompts_raw()
            mistral_params = {"model": "mistral-large-2512", "temperature": 0.3, "max_tokens": 2000}
            openrouter_params = {
                "model": os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it"),
                "temperature": 0.4,
                "max_completion_tokens": 8000,
            }

            context_cache_key = build_cache_key(
                safe_input, mistral_params["model"], prompts_raw, mistral_params
            )
            metrics_cache_key_prefix = build_cache_key(
                safe_input, openrouter_params["model"], prompts_raw, openrouter_params
            )

            # Initialize pipeline with delegated executors and UI handler
            pipeline = AnalysisPipeline(
                mistral_executor=cached_analyze_context,
                openai_metrics_executor=cached_generate_metrics,
                openai_summary_executor=get_openai_service().stream_executive_summary,
                pdf_generator=get_pdf_generator(),
                ui_handler=StreamlitUIHandler(),
            )

            # Execute full pipeline
            results = pipeline.execute(
                initiative_text=safe_input,
                context_cache_key=context_cache_key,
                metrics_cache_key_prefix=metrics_cache_key_prefix,
                params={"responsible": responsible, "company": company},
            )

            context = results["context"]
            metrics = results["metrics"]
            executive_summary = results["executive_summary"]
            artifact_bytes = results["artifact_bytes"]
            artifact_result = results["artifact_result"]
            report_id = results["report_id"]

            st.balloons()
            from utils.telemetry import record_telemetry_event

            record_telemetry_event("analysis_save_attempt")
            try:
                snapshot_id = save_snapshot(
                    initiative_text=safe_input,
                    responsible=responsible,
                    company=company,
                    context=context,
                    metrics=metrics,
                    executive_summary=executive_summary,
                    pdf_bytes=artifact_bytes,
                    artifact_result=artifact_result,
                )
                record_telemetry_event("analysis_save_success")
                st.success(f"✅ Análise salva como **Snapshot #{snapshot_id}**")
            except Exception as save_err:
                logger.error("Failed to save snapshot: %s", str(save_err))
                record_telemetry_event("analysis_save_error")
                st.warning("A análise foi gerada, mas houve um erro ao salvar no histórico.")

            render_results(
                context,
                metrics,
                artifact_bytes,
                artifact_result,
                report_id,
                snapshot_id=snapshot_id,
            )

        except Exception as e:
            logger.error("pipeline error: %s", redact_log_message(str(e)))
            from ui.styles import render_premium_state

            render_premium_state(
                "error",
                "Ops! Algo deu errado",
                "Ocorreu um erro inesperado no processamento da sua análise. "
                "Por favor, tente novamente em alguns instantes.",
                "Tentar Novamente",
            )
            if not _IS_PRODUCTION:
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
    render_footer()
