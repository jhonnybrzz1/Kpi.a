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

/* ── Cards de resultado ── */
.mf-card {
    background: rgba(26,26,36,.8);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: .75rem 0;
}
.mf-card-title {
    font-size: .7rem; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    color: #6366f1; margin-bottom: .25rem;
}
.mf-card-value { font-size: 1.1rem; font-weight: 600; color: #e2e8f0; }
.mf-card-sub { font-size: .82rem; color: #94a3b8; margin-top: .2rem; }

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
