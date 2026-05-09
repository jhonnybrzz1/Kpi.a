import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

BENCHMARKS_JSON = "data/benchmarks.json"
BASELINE_MD = "data/baseline_d7.md"
REPORT_MD = "reports/benchmarks_context.md"

# Rule 3: Deterministic normalization and EPS (tolerance)
EPS = 0.001 # 0.1 percentage point tolerance

def load_benchmarks() -> List[Dict[str, Any]]:
    if not os.path.exists(BENCHMARKS_JSON):
        return []
    with open(BENCHMARKS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def get_baseline_info() -> Dict[str, Any]:
    # Baseline for Kpi.a
    return {
        "metric": "D7 Retention",
        "value": 12.0,  # Points (0-100)
        "target": 40.0, # Points (0-100)
        "segment": "Productivity"
    }

def generate_report():
    benchmarks = load_benchmarks()
    baseline = get_baseline_info()
    
    # Rule 1: Slice Consistency Gate
    relevant = [
        b for b in benchmarks 
        if b["metric"] == baseline["metric"] 
        and baseline["segment"] in b["segment"]
        and b.get("median") is not None 
        and b.get("top_quartil") is not None
    ]
    
    if not relevant:
        status = "❌ Não emitida"
        summary = "Nenhum slice consistente encontrado para o segmento e métrica (Gate falhou)."
        comparison_table = "| Métrica | Baseline | Meta |\n| :--- | :--- | :--- |\n| D7 Retention | 12% | 40% |"
    else:
        # T3: Normalization to 0-100 points
        norm_medians = [b["median"] * 100 for b in relevant]
        norm_tops = [b["top_quartil"] * 100 for b in relevant]
        
        avg_median = sum(norm_medians) / len(relevant)
        avg_top = sum(norm_tops) / len(relevant)
        
        # Rule 1 & 2: Conditional phrasing based on comparability_score
        is_high_confidence = all(b.get("comparability_score") == "high" for b in relevant)
        
        if is_high_confidence:
            status = "✅ Validada"
            conclusion = []
            
            # Rule 3: EPS Comparison
            if (baseline["target"] - avg_median) > EPS:
                conclusion.append(f"A meta de {baseline['target']:.0f}% está **acima da mediana** ({avg_median:.1f}%).")
            
            if (avg_top - baseline["target"]) > EPS:
                conclusion.append(f"Está **abaixo do top quartil** ({avg_top:.1f}%).")
            elif (baseline["target"] - avg_top) >= -EPS:
                 conclusion.append(f"Está **no nível ou acima do top quartil** ({avg_top:.1f}%).")
            
            summary = f"Comparabilidade de alta confiança (Slice consistente). {' '.join(conclusion)}"
        else:
            status = "⚠️ Parcial"
            summary = "Valores observados apresentados. Comparabilidade limitada por fontes com score médio/baixo. Não emitimos conclusões 'acima/abaixo' por cautela (Regra 2)."

        comparison_table = f"""
| Métrica | Baseline (Kpi.a) | Mediana Mercado | Top Quartil | Meta (Target) |
| :--- | :--- | :--- | :--- | :--- |
| {baseline['metric']} | {baseline['value']:.1f}% | {avg_median:.1f}% | {avg_top:.1f}% | {baseline['target']:.1f}% |
"""

    # Generate Evidences section (T4)
    evidences = "\n".join([
        f"*   **{b['source']}**: [{b['segment']}]({b['url']}) - Acesso: {b['date_accessed']} (Def: {b.get('definition_notes', 'N/A')})" 
        for b in relevant
    ])

    report_content = f"""# Research Report: Contexto de Mercado (D7 Retention)

> **Gerado em:** {datetime.now().strftime("%d/%m/%Y")}
> **Status:** {status}

## 1. Resumo de Comparabilidade
**{summary}**

## 2. Tabela Comparativa
{comparison_table}

## 3. Evidências Usadas
{evidences if relevant else "Nenhuma evidência compatível encontrada nos arquivos locais."}

## 4. Definição Operacional (Kpi.a)
Referência detalhada em: `/data/baseline_d7.md`
O D7 Retention é medido como retorno (evento ativo) exatamente no dia 7 para novos usuários do Dia 0.

---
*Relatório gerado automaticamente pelo validador de benchmarks do Kpi.a para suporte à decisão (PRD v1.0).*
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return REPORT_MD

if __name__ == "__main__":
    path = generate_report()
    print(f"Relatório gerado em: {path}")
