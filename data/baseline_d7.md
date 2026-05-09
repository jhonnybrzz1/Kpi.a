# Definição Operacional: D7 Retention (Kpi.a)

Este documento descreve como o **D7 Retention** é calculado operacionalmente para o projeto Kpi.a e serve como base para comparação com benchmarks de mercado.

## 1. Definição da Métrica
*   **Nome:** D7 Retention (Day 7 Retention)
*   **Tipo:** N-Day Retention (Cohort-based)
*   **Denominador (Cohort):** Novos usuários que realizaram o evento "Sign Up" no Dia 0.
*   **Numerador:** Usuários do cohort que realizaram pelo menos um "Evento Ativo" exatamente no Dia 7 (janela de 24h).
*   **Evento Ativo:** Abertura do app ou conclusão de uma análise.

## 2. Baseline Atual (Estimativa)
*   **Valor:** 12%
*   **Fonte:** Estimativa conservadora baseada em logs iniciais de alpha testing (Abril 2026).
*   **Método:** Média ponderada dos últimos 30 dias de cohorts semanais.

## 3. Meta de Negócio
*   **Valor:** 40%
*   **Justificativa:** Alinhamento com o Top Quartil de ferramentas de produtividade B2B SaaS para garantir crescimento viral e sustentabilidade.
