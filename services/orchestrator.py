import logging
from typing import Any, Dict, Generator, Protocol

logger = logging.getLogger(__name__)


class UIHandler(Protocol):
    """Protocol for UI dependency inversion (Streamlit, CLI, Silent)."""

    def on_stage_start(self, stage_idx: int, message: str) -> Any:
        """Called when a pipeline stage starts. Returns a handle to update the stage later."""
        ...

    def on_stage_update(self, handle: Any, message: str, state: str) -> None:
        """Updates an existing stage handle with a new message and state."""
        ...

    def handle_stream(self, stream: Generator[str, None, None]) -> str:
        """Processes a token stream and returns the accumulated text."""
        ...

    def render_skeletons(self, stage_idx: int) -> None:
        """Renders visual loading indicators (skeletons)."""
        ...


class AnalysisPipeline:
    """
    Decoupled AI Orchestrator that manages the 4-stage sequential pipeline.
    Agnostic of UI frameworks by using the UIHandler protocol.
    """

    def __init__(
        self,
        mistral_executor,
        openai_metrics_executor,
        openai_summary_executor,
        pdf_generator,
        ui_handler: UIHandler,
    ):
        self.mistral_executor = mistral_executor
        self.openai_metrics_executor = openai_metrics_executor
        self.openai_summary_executor = openai_summary_executor
        self.pdf_generator = pdf_generator
        self.ui_handler = ui_handler

    def execute(
        self,
        initiative_text: str,
        context_cache_key: str,
        metrics_cache_key_prefix: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executes the full analysis pipeline.

        Args:
            initiative_text: The user input text.
            context_cache_key: Key for Stage 1 caching.
            metrics_cache_key_prefix: Base key for Stage 2 caching (will be salted with context).
            params: Metadata like 'responsible' and 'company'.

        Returns:
            A dictionary containing all generated artifacts and context.
        """
        import json
        from datetime import datetime

        state = {
            "initiative_text": initiative_text,
            "responsible": params.get("responsible", "N/A"),
            "company": params.get("company", "N/A"),
            "date": datetime.now().strftime("%d/%m/%Y"),
        }

        # ── Stage 1: Context ──────────────────────────────────────────────────
        h1 = self.ui_handler.on_stage_start(1, "🧠 Etapa 1/4 — Contexto (Mistral AI)...")
        self.ui_handler.render_skeletons(1)
        state["context"] = self.mistral_executor(initiative_text, context_cache_key)
        self.ui_handler.on_stage_update(h1, "✅ Contexto analisado", "complete")

        # ── Stage 2: Metrics ──────────────────────────────────────────────────
        h2 = self.ui_handler.on_stage_start(2, "📊 Etapa 2/4 — Arquitetura de Métricas...")
        self.ui_handler.render_skeletons(2)

        context_json = json.dumps(state["context"], ensure_ascii=False)
        # Salt the metrics cache key with the context to ensure re-generation if context changes
        metrics_cache_key = f"{metrics_cache_key_prefix}:{hash(context_json)}"

        state["metrics"] = self.openai_metrics_executor(
            initiative_text, context_json, metrics_cache_key
        )
        self.ui_handler.on_stage_update(h2, "✅ Métricas geradas", "complete")

        # ── Stage 3: Summary ──────────────────────────────────────────────────
        h3 = self.ui_handler.on_stage_start(3, "✍️ Etapa 3/4 — Resumo Executivo...")
        stream = self.openai_summary_executor(initiative_text, state["context"], state["metrics"])
        state["executive_summary"] = self.ui_handler.handle_stream(stream)
        self.ui_handler.on_stage_update(h3, "✅ Resumo gerado", "complete")

        # ── Stage 4: PDF ──────────────────────────────────────────────────────
        h4 = self.ui_handler.on_stage_start(4, "📄 Etapa 4/4 — Relatório PDF...")
        report_data = {
            "initiative_description": initiative_text,
            "responsible": state["responsible"],
            "company": state["company"],
            "date": state["date"],
            "context_analysis": state["context"],
            "metrics_analysis": state["metrics"],
            "executive_summary": state["executive_summary"],
        }
        artifact_result, artifact_bytes, report_id = (
            self.pdf_generator.generate_report_with_fallback(report_data)
        )
        state["artifact_result"] = artifact_result
        state["artifact_bytes"] = artifact_bytes
        state["report_id"] = report_id

        if artifact_result == "pdf_only":
            self.ui_handler.on_stage_update(h4, "✅ Relatório pronto", "complete")
        elif artifact_result == "markdown_only":
            self.ui_handler.on_stage_update(h4, "⚠️ PDF indisponível — Markdown gerado", "complete")
        else:
            self.ui_handler.on_stage_update(h4, "❌ Relatório não disponível", "error")

        return state
