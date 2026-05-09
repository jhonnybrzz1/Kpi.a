import json
from typing import Any, Dict

import streamlit as st


def render_results(context: Dict[str, Any], metrics: Dict[str, Any], pdf_bytes: bytes) -> None:
    st.markdown("## Análise Estratégica de Métricas")

    with st.expander("🧠 Contexto e Valor Entregue", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tipo", context.get("tipo", "N/A"))
        m2.metric("Game", context.get("business_game", "N/A"))
        m3.metric("Objetivo", context.get("objetivo", "N/A"))
        m4.metric("Etapa AARRR", context.get("etapa_funil", "N/A"))
        st.success(f"📝 **Resumo do PRD (Objetivo):** {context.get('resumo_prd', 'N/A')}")
        with st.expander("📊 Dados Identificados", expanded=True):
            data = context.get("dados_atuais", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    st.write(data)
            if isinstance(data, dict):
                for k, v in data.items():
                    st.write(f"**{k.replace('_', ' ').title()}:** {v}")

    with st.expander("🎯 North Star Metric", expanded=True):
        ns = metrics.get("north_star", {})
        st.markdown(f"### {ns.get('nome', 'N/A')}")
        st.write(ns.get("justificativa", ""))
        st.code(f"Fórmula: {ns.get('definicao', 'N/A')}", language=None)
        st.write("**Validação SMART:**", ", ".join(ns.get("validacao_smart", [])))

    with st.expander("📈 L1 Health Indicators (Saúde do Produto)", expanded=True):
        for l1 in metrics.get("l1_health_indicators", []):
            c1, c2, c3 = st.columns([1, 2, 2])
            c1.markdown(f"**{l1.get('pilar')}**")
            c2.markdown(f"**{l1.get('metrica')}**")
            c3.caption(f"🎯 Meta: {l1.get('meta_sugerida')}")
            st.write(f"_{l1.get('por_que_importa')}_")
            st.markdown("---")

    with st.expander("🔍 L2 Diagnostic Metrics (Investigação)", expanded=False):
        for l2 in metrics.get("l2_diagnostic_metrics", []):
            st.write(f"🔗 **Vinculada à L1:** {l2.get('vinculo_l1')}")
            st.write(f"**Métrica:** {l2.get('metrica')}")
            st.warning(f"⚠️ **Ação se cair:** {l2.get('acao_se_cair')}")
            st.markdown("---")

    with st.expander("🏆 OKRs de Resultado (Outcomes)", expanded=True):
        for okr in metrics.get("okrs", []):
            st.markdown(f"#### 🎯 {okr.get('objetivo')}")
            for kr in okr.get("key_results", []):
                st.write(f"✅ **{kr.get('resultado')}**")
                st.caption(f"Baseline: {kr.get('baseline')} | Meta: {kr.get('meta')}")
            st.markdown("---")

    with st.expander("⚖️ Contra-Métricas (Anti-Fraude)", expanded=False):
        for cm in metrics.get("counter_metrics", []):
            st.write(f"🛡️ **{cm.get('nome')}**")
            st.write(f"**Protege contra:** {cm.get('protege_contra')}")
            st.caption(f"❗ Trade-off: {cm.get('trade_off')}")

    with st.expander("🛠️ Guia de Implementação", expanded=False):
        imp = metrics.get("implementacao", {})
        st.write("**Ferramentas:**", ", ".join(imp.get("ferramentas", [])))
        st.write("**Visualização:**", imp.get("visualizacao", ""))
        for q in imp.get("queries_exemplo", []):
            st.code(q, language="sql")

    st.download_button(
        "📄 Baixar Relatório PDF",
        data=pdf_bytes,
        file_name="MetricFlow_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
