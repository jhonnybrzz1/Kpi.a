import streamlit as st

from utils.examples import INITIATIVE_EXAMPLES

_STEPS = [
    ("1", "Descreva a Iniciativa", "Detalhe seu projeto ou funcionalidade"),
    ("2", "Análise Estratégica", "IA define contexto e North Star"),
    ("3", "Hierarchy Review", "Métricas L1/L2 e Health Indicators"),
    ("4", "Actionable OKRs", "Resultados de negócio (Outcomes)"),
]


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("#### Como Funciona")
        html_steps = "".join(
            f'<div class="mf-step">'
            f'<div class="mf-step-num">{num}</div>'
            f'<div class="mf-step-body"><strong>{title}</strong><span>{desc}</span></div>'
            f"</div>"
            for num, title, desc in _STEPS
        )
        st.markdown(html_steps, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Exemplos de Iniciativas")

        categories = list(set(ex["category"] for ex in INITIATIVE_EXAMPLES.values()))
        selected_category = st.selectbox(
            "Categoria", ["Todas"] + categories, index=0, label_visibility="collapsed"
        )

        filtered = (
            INITIATIVE_EXAMPLES
            if selected_category == "Todas"
            else {
                k: v
                for k, v in INITIATIVE_EXAMPLES.items()
                if v.get("category") == selected_category
            }
        )

        for key, example in filtered.items():
            if st.button(example["title"], use_container_width=True, key=f"btn_{key}"):
                st.session_state["example_text"] = example["description"]
                st.rerun()

        # ── Análises Recentes ─────────────────────────────────────────────
        from utils.history import get_history

        history = get_history()
        if history:
            st.markdown("---")
            st.markdown("#### 🕘 Análises Recentes")

            # Comparison selection
            if "compare_ids" not in st.session_state:
                st.session_state["compare_ids"] = []

            for item in history:
                snapshot_id = item["snapshot_id"]
                saved_at = item["saved_at"][:16].replace("T", " ")
                label = (
                    f"{item['initiative_preview'][:40]}…"
                    if len(item["initiative_preview"]) > 40
                    else item["initiative_preview"]
                )

                # Checkbox for comparison
                is_selected = snapshot_id in st.session_state["compare_ids"]
                if st.checkbox(
                    f"{label}",
                    value=is_selected,
                    key=f"chk_{snapshot_id}",
                    help=f"Salvo em: {saved_at}",
                ):
                    if snapshot_id not in st.session_state["compare_ids"]:
                        if len(st.session_state["compare_ids"]) < 2:
                            st.session_state["compare_ids"].append(snapshot_id)
                        else:
                            st.warning("Selecione apenas 2 para comparar.")
                            # Force uncheck by rerunning or handled by Streamlit checkbox state
                else:
                    if snapshot_id in st.session_state["compare_ids"]:
                        st.session_state["compare_ids"].remove(snapshot_id)

                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.caption(f"🗓 {saved_at}")
                with col2:
                    if st.button(
                        "👁️",
                        key=f"restore_{snapshot_id}",
                        help="Ver detalhes desta análise",
                    ):
                        from utils.telemetry import record_telemetry_event

                        record_telemetry_event("history_reload_clicked")
                        st.session_state["_restore_snapshot"] = item
                        st.rerun()

            if len(st.session_state["compare_ids"]) == 2:
                st.markdown("---")
                if st.button("⚖️ Comparar Selecionados", type="primary", use_container_width=True):
                    from utils.telemetry import record_telemetry_event

                    record_telemetry_event("compare_started")
                    st.session_state["_view"] = "compare"
                    st.rerun()
            elif len(st.session_state["compare_ids"]) == 1:
                st.info("Selecione mais uma para comparar.")
        else:
            st.markdown("---")
            st.caption("📭 Nenhuma análise salva ainda.")
