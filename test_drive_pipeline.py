import logging
import json
from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.orchestrator import AnalysisPipeline, UIHandler

# Setup basic logging to see the refinement process
logging.basicConfig(level=logging.INFO, format="%(message)s")

class ConsoleUIHandler(UIHandler):
    def on_stage_start(self, stage_idx, message):
        print(f"\n[Stage {stage_idx}] {message}")
        return None
    def on_stage_update(self, handle, message, state):
        print(f"  -> {message} ({state})")
    def handle_stream(self, stream):
        print("  -> (Streaming Summary...)", end="", flush=True)
        text = ""
        for chunk in stream:
            text += chunk
        print(" Done.")
        return text
    def render_skeletons(self, stage_idx):
        pass

def test_drive():
    print("🚀 Iniciando Teste Real do MetricFlow AI (Pipeline Refatorado)")
    
    from unittest.mock import MagicMock
    mock_pdf = MagicMock()
    mock_pdf.generate_report_with_fallback.return_value = ("markdown_only", b"", "test-id")

    mistral = MistralService()
    openai = OpenAIService()

    # Wrap services to match the expected executor signature
    def mistral_executor(text, key):
        print("  -> (Mocking Mistral Stage 1)")
        return {
            "tipo": "funcionalidade",
            "business_game": "transaction",
            "objetivo": "receita",
            "etapa_funil": "retencao",
            "complexidade": "media",
            "area_impacto": ["e-commerce", "growth"],
            "valor_entregue": "Redução de churn de carrinho e aumento de conversão.",
            "resumo_prd": "Recomendações personalizadas para recuperação de vendas.",
            "dados_atuais": "Não mencionado",
            "justificativa": "Recuperação de carrinhos é um pilar clássico de transação.",
            "palavras_chave": ["IA", "recomendação", "carrinho"],
            "confidence": 0.9
        }
    
    def openai_metrics_executor(text, context_json, key):
        import json
        return openai.generate_metrics(text, json.loads(context_json))

    pipeline = AnalysisPipeline(
        mistral_executor=mistral_executor,
        openai_metrics_executor=openai_metrics_executor,
        openai_summary_executor=openai.stream_executive_summary,
        pdf_generator=mock_pdf,
        ui_handler=ConsoleUIHandler()
    )

    # Use a real (but simple) initiative
    initiative = "Implementar um sistema de recomendação baseado em IA para aumentar a conversão de carrinhos abandonados em um e-commerce de moda."
    
    print(f"\nINICIATIVA: {initiative}")
    
    try:
        # Mocking cache keys and params for the test
        results = pipeline.execute(
            initiative_text=initiative,
            context_cache_key="test_key_v1",
            metrics_cache_key_prefix="test_metrics_v1",
            params={"responsible": "AI Tester", "company": "MetricFlow Lab"}
        )
        
        print("\n" + "="*50)
        print("✅ RESULTADO DA ANÁLISE")
        print("="*50)
        print(f"North Star: {results['metrics']['north_star']['nome']}")
        print(f"Definição: {results['metrics']['north_star']['definicao']}")
        print("\nOKRs Principais:")
        for okr in results['metrics']['okrs'][:2]:
            print(f"- {okr['objetivo']}")
            for kr in okr['key_results']:
                print(f"  * KR: {kr['resultado']} ({kr['baseline']} -> {kr['meta']})")
        
        print("\nResumo Executivo:")
        print(results['executive_summary'])
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    # We need to monkeypatch pdf_generator since we passed None
    from unittest.mock import MagicMock
    mock_pdf = MagicMock()
    mock_pdf.generate_report_with_fallback.return_value = ("markdown_only", b"", "test-id")
    
    # Run test
    import os
    os.environ["PYTHONPATH"] = "."
    test_drive()
