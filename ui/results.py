import json
from typing import Any, Dict

import streamlit as st

from utils.overrides import delete_overrides, generate_item_key, get_overrides, save_override
from utils.telemetry import record_telemetry_event


def render_results(
    context: Dict[str, Any],
    metrics: Dict[str, Any],
    artifact_bytes: bytes,
    artifact_result: str = "pdf_only",
    report_id: str = "",
    snapshot_id: str = "",
) -> None:
    st.markdown("## Análise Estratégica de Métricas")

    overrides = get_overrides(snapshot_id) if snapshot_id else {}

    # ── Actions ─────────────────────────────────────────────────────────────
    if snapshot_id and overrides:
        if st.button(
            "🔄 Resetar Edições Manuais",
            help="Remove todos os ajustes manuais e volta para a sugestão original da IA",
        ):
            delete_overrides(snapshot_id)
            record_telemetry_event("reanalyze_clicked")
            st.success("Edições resetadas com sucesso!")
            st.rerun()

    with st.expander("🧠 Contexto e Valor Entregue", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tipo", context.get("tipo", "N/A"), help="Classificação da iniciativa")
        m2.metric("Game", context.get("business_game", "N/A"), help="Foco estratégico de negócio")
        m3.metric("Objetivo", context.get("objetivo", "N/A"), help="Principal driver de valor")
        m4.metric(
            "Etapa AARRR",
            context.get("etapa_funil", "N/A"),
            help="Posicionamento no funil de produto",
        )

        st.markdown(
            '<div class="mf-premium-metric" '
            'style="margin-top:1.5rem; margin-bottom:1.5rem;">'
            "<strong>📝 Resumo do PRD:</strong>"
            f'<br>{context.get("resumo_prd", "N/A")}</div>',
            unsafe_allow_html=True,
        )
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
        st.markdown(
            f"""
            <div class="mf-card">
                <div class="mf-card-title">North Star Metric</div>
                <div class="mf-card-value">{ns.get("nome", "N/A")}</div>
                <div class="mf-card-sub">{ns.get("justificativa", "")}</div>
                <div style="margin-top:1rem; padding:0.75rem; background:rgba(0,0,0,0.2);
                            border-radius:8px; font-family:monospace; color:#818cf8;">
                    Fórmula: {ns.get("definicao", "N/A")}
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.write("**Validação SMART:**", ", ".join(ns.get("validacao_smart", [])))

    with st.expander("📈 L1 Health Indicators (Saúde do Produto)", expanded=True):
        for idx, l1 in enumerate(metrics.get("l1_health_indicators", [])):
            item_key = generate_item_key("l1", l1.get("pilar", ""), l1.get("metrica", ""))
            item_overrides = overrides.get(item_key, {})

            # Field: metrica
            original_metrica = l1.get("metrica", "N/A")
            display_metrica = item_overrides.get("metrica", original_metrica)
            is_edited = "metrica" in item_overrides

            c1, c2, c3, c4 = st.columns([1, 2, 2, 0.5])
            c1.markdown(f"**{l1.get('pilar')}**")

            editing_key = f"edit_l1_{item_key}"
            if st.session_state.get("editing_item") == editing_key:
                new_val = c2.text_input(
                    "Nome da Métrica", value=display_metrica, key=f"input_{editing_key}"
                )
                col_s, col_c = c2.columns(2)
                if col_s.button("✅", key=f"save_{editing_key}"):
                    if new_val.strip() and new_val != original_metrica:
                        save_override(snapshot_id, item_key, "metrica", new_val.strip())
                        record_telemetry_event("edit_save_success")
                    elif new_val == original_metrica:
                        # If value is same as original, we could remove the override
                        pass
                    st.session_state.editing_item = None
                    st.rerun()
                if col_c.button("❌", key=f"cancel_{editing_key}"):
                    st.session_state.editing_item = None
                    st.rerun()
            else:
                label = display_metrica
                if is_edited:
                    label += " ✏️"
                c2.markdown(f"**{label}**")
                if c4.button("📝", key=f"btn_{editing_key}", help="Editar nome da métrica"):
                    st.session_state.editing_item = editing_key
                    st.rerun()

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
        for okr_idx, okr in enumerate(metrics.get("okrs", [])):
            st.markdown(f"#### 🎯 {okr.get('objetivo')}")
            for kr_idx, kr in enumerate(okr.get("key_results", [])):
                item_key = generate_item_key("kr", okr.get("objetivo", ""), kr.get("resultado", ""))
                item_overrides = overrides.get(item_key, {})

                if item_overrides.get("deleted") == "true":
                    continue

                original_meta = str(kr.get("meta", "N/A"))
                display_meta = item_overrides.get("meta", original_meta)
                is_edited = "meta" in item_overrides

                editing_key = f"edit_kr_{item_key}"

                col_kr, col_edit = st.columns([0.8, 0.2])

                with col_kr:
                    st.write(f"✅ **{kr.get('resultado')}**")
                    if st.session_state.get("editing_item") == editing_key:
                        new_meta = st.text_input(
                            "Ajustar Meta", value=display_meta, key=f"input_{editing_key}"
                        )
                        col_s, col_c = st.columns([0.2, 0.2, 0.6])
                        if col_s.button("✅", key=f"save_{editing_key}"):
                            if new_meta.strip() and new_meta != original_meta:
                                save_override(snapshot_id, item_key, "meta", new_meta.strip())
                                record_telemetry_event("edit_save_success")
                            st.session_state.editing_item = None
                            st.rerun()
                        if col_c.button("❌", key=f"cancel_{editing_key}"):
                            st.session_state.editing_item = None
                            st.rerun()
                    else:
                        meta_label = f"Meta: {display_meta}"
                        if is_edited:
                            meta_label += " ✏️"
                        st.caption(f"Baseline: {kr.get('baseline')} | {meta_label}")

                with col_edit:
                    ced1, ced2 = st.columns(2)
                    if ced1.button("📝", key=f"btn_{editing_key}", help="Editar meta"):
                        st.session_state.editing_item = editing_key
                        st.rerun()
                    if ced2.button("🗑️", key=f"del_{item_key}", help="Remover Key Result"):
                        save_override(snapshot_id, item_key, "deleted", "true")
                        record_telemetry_event("edit_save_success")
                        st.rerun()

            # Adicionar novo KR
            okr_key = generate_item_key("okr", okr.get("objetivo", ""))
            add_kr_key = f"add_kr_{okr_key}"
            if st.session_state.get("editing_item") == add_kr_key:
                new_res = st.text_input("Novo Resultado", key=f"input_res_{add_kr_key}")
                new_meta = st.text_input("Meta", key=f"input_meta_{add_kr_key}")
                col_s, col_c = st.columns([0.2, 0.2, 0.6])
                if col_s.button("Salvar KR", key=f"save_{add_kr_key}"):
                    if new_res.strip():
                        added_krs = json.loads(overrides.get(okr_key, {}).get("added_krs", "[]"))
                        added_krs.append(
                            {"resultado": new_res, "meta": new_meta, "baseline": "N/A"}
                        )
                        save_override(snapshot_id, okr_key, "added_krs", json.dumps(added_krs))
                        record_telemetry_event("edit_save_success")
                    st.session_state.editing_item = None
                    st.rerun()
                if col_c.button("Cancelar", key=f"cancel_{add_kr_key}"):
                    st.session_state.editing_item = None
                    st.rerun()
            else:
                if st.button("➕ Adicionar KR", key=f"btn_{add_kr_key}"):
                    st.session_state.editing_item = add_kr_key
                    st.rerun()

            # Renderizar KRs adicionados manualmente
            added_krs = json.loads(overrides.get(okr_key, {}).get("added_krs", "[]"))
            for akr_idx, akr in enumerate(added_krs):
                col_akr, col_adel = st.columns([0.9, 0.1])
                with col_akr:
                    st.write(f"✅ **{akr.get('resultado')}** ✏️")
                    st.caption(f"Baseline: {akr.get('baseline')} | Meta: {akr.get('meta')}")
                with col_adel:
                    if st.button(
                        "🗑️", key=f"del_added_{okr_key}_{akr_idx}", help="Remover KR manual"
                    ):
                        added_krs.pop(akr_idx)
                        save_override(snapshot_id, okr_key, "added_krs", json.dumps(added_krs))
                        st.rerun()
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

    st.markdown("---")
    st.markdown(
        '<div style="padding: 1.5rem; background: rgba(99,102,241,0.05); '
        'border-radius: 12px; border: 1px solid rgba(99,102,241,0.1);">',
        unsafe_allow_html=True,
    )
    st.markdown("### 📥 Exportar Relatório")

    if artifact_result == "pdf_only":
        st.download_button(
            "📄 Baixar Relatório PDF Completo",
            data=artifact_bytes,
            file_name="MetricFlow_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    elif artifact_result == "markdown_only":
        st.warning(f"⚠️ PDF indisponível (ID: `{report_id}`). Baixe o relatório em Markdown:")
        st.download_button(
            "📝 Baixar Relatório Markdown",
            data=artifact_bytes,
            file_name="MetricFlow_Report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        st.error(f"❌ Relatório não disponível (ID: `{report_id}`). Tente novamente.")

    st.markdown("</div>", unsafe_allow_html=True)
