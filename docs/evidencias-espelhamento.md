# Evidências de Espelhamento Front↔Backend

**Data:** 09/05/2026

## Smoke Test - Ações Críticas (Tela Âncora)

| Ação | Resultado Esperado | Resultado Observado | Status |
| :--- | :--- | :--- | :--- |
| **Gerar Análise** | Processar via OpenAI/Mistral e exibir resultados. | Sucesso. Integrado com Skeletons e Status. | ✅ OK |
| **Restaurar Snapshot** | Carregar dados do SQLite via Sidebar. | Sucesso. Todos os campos (Incl. Resp/Empresa) restaurados. | ✅ OK |
| **Editar Métrica** | Persistir alteração no SQLite (overrides). | Sucesso. Badge ✏️ exibido e persiste após F5. | ✅ OK |
| **Comparar** | Exibir 2 snapshots lado a lado. | Sucesso. Validação de contrato v1 impede dados parciais. | ✅ OK |
| **Baixar PDF** | Gerar binário e disparar download. | Sucesso. Fallback para Markdown ativo. | ✅ OK |

## Observações
- O componente de **Auto-save** foi intencionalmente mantido fora conforme PRD para evitar bugs de concorrência no SQLite local do Streamlit.
- O tempo de carregamento percebido melhorou com o uso de `mf-skeleton` durante as etapas bloqueantes da IA.
