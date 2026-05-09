import streamlit as st

_CSS = """
<style>
/* ── Tipografia base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.mf-header {
    padding: 2.5rem 2rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
    border: 1px solid rgba(99,102,241,.35);
    text-align: center;
    margin-bottom: 2rem;
}
.mf-header h1 {
    margin: 0 0 .4rem;
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -.5px;
}
.mf-header p { margin: 0; color: #a5b4fc; font-size: 1rem; }
.mf-badge {
    display: inline-block;
    margin-top: .8rem;
    padding: .25rem .75rem;
    border-radius: 999px;
    background: rgba(99,102,241,.25);
    border: 1px solid rgba(99,102,241,.5);
    color: #c7d2fe;
    font-size: .75rem;
    font-weight: 500;
    letter-spacing: .5px;
}

/* ── Sidebar ── */
.mf-step {
    display: flex;
    align-items: flex-start;
    gap: .75rem;
    padding: .75rem 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.mf-step:last-child { border-bottom: none; }
.mf-step-num {
    flex-shrink: 0;
    width: 28px; height: 28px;
    border-radius: 50%;
    background: rgba(99,102,241,.2);
    border: 1px solid rgba(99,102,241,.4);
    color: #a5b4fc;
    font-size: .75rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}
.mf-step-body { flex: 1; }
.mf-step-body strong { display: block; color: #e2e8f0; font-size: .85rem; margin-bottom: .15rem; }
.mf-step-body span { color: #94a3b8; font-size: .78rem; }

/* ── Skeleton Loading ── */
@keyframes skeleton-shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: calc(200px + 100%) 0; }
}
.mf-skeleton {
    height: 20px;
    width: 100%;
    background: #1e1b4b;
    background-image: linear-gradient(90deg, #1e1b4b 0px, #312e81 40px, #1e1b4b 80px);
    background-size: 200px 100%;
    background-repeat: no-repeat;
    border-radius: 4px;
    animation: skeleton-shimmer 1.5s infinite linear;
    margin-bottom: 0.5rem;
}

/* ── Standard States (Premium) ── */
.mf-empty-state, .mf-error-state {
    padding: 3rem 2rem;
    text-align: center;
    border-radius: 16px;
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(99,102,241,0.3);
}
.mf-empty-state h3, .mf-error-state h3 { color: #e2e8f0; margin-bottom: 1rem; }
.mf-empty-state p, .mf-error-state p { color: #94a3b8; max-width: 400px; margin: 0 auto 1.5rem; }

/* ── Cards de resultado ── */
.mf-card {
    background: rgba(30,30,46,0.5);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.3s ease;
}
.mf-card:hover {
    border-color: rgba(99,102,241,0.4);
    background: rgba(30,30,46,0.7);
    transform: translateY(-2px);
}
.mf-card-title {
    font-size: 0.75rem; font-weight: 600;
    letter-spacing: 1.2px; text-transform: uppercase;
    color: #818cf8; margin-bottom: 0.5rem;
}
.mf-card-value { font-size: 1.4rem; font-weight: 700; color: #f8fafc; }
.mf-card-sub { font-size: 0.875rem; color: #94a3b8; margin-top: 0.4rem; line-height: 1.5; }

/* ── Premium Metric ── */
.mf-premium-metric {
    background: linear-gradient(180deg, rgba(99,102,241,0.1) 0%, rgba(99,102,241,0) 100%);
    border-left: 4px solid #6366f1;
    padding-left: 1.25rem;
}

/* ── Upload info box ── */
.mf-upload-info {
    background: rgba(99,102,241,.08);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 8px;
    padding: .75rem 1rem;
    color: #a5b4fc; font-size: .85rem;
    margin-bottom: .75rem;
}

/* ── Footer ── */
.mf-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(255,255,255,.06);
    color: #475569; font-size: .82rem;
}
.mf-footer strong { color: #6366f1; }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_premium_state(
    state_type: str, title: str, message: str, button_label: str = None
) -> None:
    """Render a premium empty or error state."""
    class_name = "mf-empty-state" if state_type == "empty" else "mf-error-state"
    st.markdown(
        f"""
        <div class="{class_name}">
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if button_label:
        if st.button(button_label, type="primary", use_container_width=True):
            st.rerun()


def render_skeletons(count: int = 3) -> None:
    """Render shimmering skeleton placeholders."""
    for _ in range(count):
        st.markdown('<div class="mf-skeleton"></div>', unsafe_allow_html=True)
        st.markdown('<div class="mf-skeleton" style="width:70%;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="mf-skeleton" style="width:40%; margin-bottom:1.5rem;"></div>',
            unsafe_allow_html=True,
        )
