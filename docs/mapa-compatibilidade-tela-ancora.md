# Mapa de Compatibilidade - Tela Âncora (Resultados)

**Tela Âncora:** Painel de Resultados (`ui/results.py`)

| Ação Crítica | Componente Front | Recurso Backend (Endpoint/Service) | Status | Observação |
| :--- | :--- | :--- | :--- | :--- |
| Gerar Análise | Botão "🚀 Gerar Análise" | `OpenAIService.generate_metrics` | ✅ Mantém | Fluxo principal validado. |
| Restaurar Histórico | Botão "👁️" (Sidebar) | `utils/history.py:get_history` | ✅ Mantém | Persistência via SQLite. |
| Editar Métrica L1 | Botão "📝" (L1 Card) | `utils/overrides.py:save_override` | ✅ Mantém | Implementado no ciclo anterior. |
| Ajustar Meta KR | Botão "📝" (KR List) | `utils/overrides.py:save_override` | ✅ Mantém | Implementado no ciclo anterior. |
| Resetar Edições | Botão "🔄 Resetar Edições" | `utils/overrides.py:delete_overrides` | ✅ Mantém | Funciona via snapshot_id. |
| Baixar PDF | Botão "📄 Baixar Relatório PDF" | `PDFGenerator.generate_report_with_fallback` | ✅ Mantém | Integrado ao fluxo de salvamento. |
| Comparar Análises | Botão "⚖️ Comparar" | `ui/comparison.py` | ✅ Mantém | Snapshot Contract v1 ativo. |
| Gerar Research Report | Botão "Gerar Research" (Dev) | `utils/benchmarks.py:generate_report` | ✅ Mantém | Funcionalidade de benchmark. |
| Ver por ID | URL `?id=XXXX` | `app.py` -> `utils/history.py` | ✅ Mantém | Suporte a query params. |

## Ações Não Suportadas / Removidas
- **Auto-save:** Removido da proposta inicial para evitar inconsistência (PRD prioriza salvar explícito).
- **Edit Context:** O contexto (tipo, etapa) é read-only após a geração no MVP.
