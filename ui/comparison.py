from typing import Any, Dict, List

import streamlit as st


def render_comparison(snapshots: List[Dict[str, Any]]) -> None:
    """Render side-by-side comparison of 2 snapshots."""
    if len(snapshots) != 2:
        st.error("A comparação requer exatamente 2 análises.")
        return

    st.markdown("## ⚖️ Comparação Lado a Lado")

    if st.button("⬅️ Voltar"):
        st.session_state["_view"] = "main"
        st.rerun()

    s1, s2 = snapshots[0], snapshots[1]
    p1, p2 = s1["payload"], s2["payload"]
    c1, c2 = p1["context"], p2["context"]
    m1, m2 = p1["metrics"], p2["metrics"]

    # ── Header ──────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Análise A")
        st.info(f"**Iniciativa:** {p1.get('initiative_text', 'N/A')[:100]}...")
        st.caption(f"Salvo em: {s1['saved_at'][:16]}")
    with col2:
        st.subheader("Análise B")
        st.info(f"**Iniciativa:** {p2.get('initiative_text', 'N/A')[:100]}...")
        st.caption(f"Salvo em: {s2['saved_at'][:16]}")

    st.markdown("---")

    # ── Strategic Context ────────────────────────────────────────────────────
    st.markdown("### 🧠 Contexto Estratégico")
    cl1, cl2 = st.columns(2)
    with cl1:
        st.write(f"**Tipo:** {c1.get('tipo', 'N/A')}")
        st.write(f"**Etapa AARRR:** {c1.get('etapa_funil', 'N/A')}")
        st.write(f"**Complexidade:** {c1.get('complexidade', 'N/A')}")
    with cl2:
        st.write(f"**Tipo:** {c2.get('tipo', 'N/A')}")
        st.write(f"**Etapa AARRR:** {c2.get('etapa_funil', 'N/A')}")
        st.write(f"**Complexidade:** {c2.get('complexidade', 'N/A')}")

    st.markdown("---")

    # ── North Star Metric ────────────────────────────────────────────────────
    st.markdown("### 🎯 North Star Metric")
    ns1, ns2 = m1.get("north_star", {}), m2.get("north_star", {})
    nl1, nl2 = st.columns(2)
    with nl1:
        st.markdown(f"**{ns1.get('nome', 'N/A')}**")
        st.caption(ns1.get("definicao", "N/A"))
    with nl2:
        st.markdown(f"**{ns2.get('nome', 'N/A')}**")
        st.caption(ns2.get("definicao", "N/A"))

    st.markdown("---")

    # ── Key Results Comparison ──────────────────────────────────────────────
    st.markdown("### 🏆 Comparação de OKRs")
    okrs1, okrs2 = m1.get("okrs", []), m2.get("okrs", [])

    # Simple list display
    ol1, ol2 = st.columns(2)
    with ol1:
        for okr in okrs1:
            st.markdown(f"**{okr.get('objetivo')}**")
            for kr in okr.get("key_results", []):
                st.caption(f"✅ {kr.get('resultado')} (Meta: {kr.get('meta')})")
    with ol2:
        for okr in okrs2:
            st.markdown(f"**{okr.get('objetivo')}**")
            for kr in okr.get("key_results", []):
                st.caption(f"✅ {kr.get('resultado')} (Meta: {kr.get('meta')})")

    st.markdown("---")
    from utils.telemetry import record_telemetry_event

    record_telemetry_event("compare_completed")
