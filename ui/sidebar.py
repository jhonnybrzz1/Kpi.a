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
            f'</div>'
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
            INITIATIVE_EXAMPLES if selected_category == "Todas"
            else {k: v for k, v in INITIATIVE_EXAMPLES.items() if v.get("category") == selected_category}
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
            for item in history:
                saved_at = item["saved_at"][:16].replace("T", " ")
                label = f"{item['initiative_preview'][:40]}…" if len(item["initiative_preview"]) > 40 else item["initiative_preview"]
                st.caption(f"🗓 {saved_at}")
                if st.button(
                    f"Ver análise",
                    key=f"restore_{item['snapshot_id']}",
                    use_container_width=True,
                    help=label,
                ):
                    st.session_state["_restore_snapshot"] = item["payload"]
                    st.rerun()
