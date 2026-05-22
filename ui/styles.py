import streamlit as st

_CSS = """
<style>
/* ── Tipografia base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ── Animações suaves ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

/* ── Header Premium ── */
.mf-header {
    padding: 3rem 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
    border: 1px solid rgba(99,102,241,.4);
    box-shadow: 0 20px 60px rgba(99,102,241,.15), 0 0 0 1px rgba(255,255,255,.05) inset;
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
    animation: fadeIn 0.6s ease-out;
}

.mf-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

.mf-header h1 {
    margin: 0 0 .6rem;
    font-size: 2.8rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -1px;
    text-shadow: 0 2px 20px rgba(99,102,241,.5);
    position: relative;
    z-index: 1;
}

.mf-header p {
    margin: 0;
    color: #c7d2fe;
    font-size: 1.1rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

.mf-badge {
    display: inline-block;
    margin-top: 1rem;
    padding: .4rem 1rem;
    border-radius: 999px;
    background: rgba(255,255,255,.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,.2);
    color: #fff;
    font-size: .8rem;
    font-weight: 600;
    letter-spacing: .5px;
    box-shadow: 0 4px 12px rgba(0,0,0,.1);
    position: relative;
    z-index: 1;
    transition: all 0.3s ease;
}

.mf-badge:hover {
    background: rgba(255,255,255,.15);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,.15);
}

/* ── Sidebar Premium ── */
.mf-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    margin-bottom: 0.75rem;
    background: rgba(30,30,46,0.4);
    border: 1px solid rgba(99,102,241,.15);
    border-radius: 12px;
    transition: all 0.3s ease;
    animation: slideIn 0.4s ease-out;
}

.mf-step:hover {
    background: rgba(30,30,46,0.6);
    border-color: rgba(99,102,241,.3);
    transform: translateX(4px);
}

.mf-step:last-child { margin-bottom: 0; }

.mf-step-num {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: 2px solid rgba(255,255,255,.2);
    color: #fff;
    font-size: .85rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(99,102,241,.3);
    transition: all 0.3s ease;
}

.mf-step:hover .mf-step-num {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(99,102,241,.4);
}

.mf-step-body {
    flex: 1;
    padding-top: 2px;
}

.mf-step-body strong {
    display: block;
    color: #f8fafc;
    font-size: .95rem;
    margin-bottom: .25rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}

.mf-step-body span {
    color: #cbd5e1;
    font-size: .85rem;
    line-height: 1.4;
}

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
    padding: 4rem 2rem;
    text-align: center;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(30,30,46,0.6) 0%, rgba(30,30,46,0.4) 100%);
    border: 2px dashed rgba(99,102,241,0.3);
    animation: fadeIn 0.6s ease-out;
    position: relative;
    overflow: hidden;
}

.mf-empty-state::before, .mf-error-state::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.1), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

.mf-empty-state h3, .mf-error-state h3 {
    color: #f8fafc;
    margin-bottom: 1rem;
    font-size: 1.5rem;
    font-weight: 700;
}

.mf-empty-state p, .mf-error-state p {
    color: #cbd5e1;
    max-width: 500px;
    margin: 0 auto 2rem;
    font-size: 1rem;
    line-height: 1.6;
}

/* ── Success/Info Messages ── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 12px !important;
    border-left: 4px solid !important;
    padding: 1rem 1.25rem !important;
    animation: slideIn 0.4s ease-out !important;
}

.stSuccess {
    background: linear-gradient(
        135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.05) 100%
    ) !important;
    border-left-color: #10b981 !important;
}

.stInfo {
    background: linear-gradient(
        135deg, rgba(99,102,241,0.1) 0%, rgba(99,102,241,0.05) 100%
    ) !important;
    border-left-color: #6366f1 !important;
}

.stWarning {
    background: linear-gradient(
        135deg, rgba(245,158,11,0.1) 0%, rgba(245,158,11,0.05) 100%
    ) !important;
    border-left-color: #f59e0b !important;
}

.stError {
    background: linear-gradient(
        135deg, rgba(239,68,68,0.1) 0%, rgba(239,68,68,0.05) 100%
    ) !important;
    border-left-color: #ef4444 !important;
}

/* ── Cards de resultado Premium ── */
.mf-card {
    background: linear-gradient(135deg, rgba(30,30,46,0.6) 0%, rgba(30,30,46,0.4) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px rgba(0,0,0,.1);
    position: relative;
    overflow: hidden;
    animation: slideIn 0.5s ease-out;
}

.mf-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #6366f1);
    background-size: 200% 100%;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.mf-card:hover {
    border-color: rgba(99,102,241,0.5);
    background: linear-gradient(135deg, rgba(30,30,46,0.8) 0%, rgba(30,30,46,0.6) 100%);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,102,241,.2);
}

.mf-card:hover::before {
    opacity: 1;
}

.mf-card-title {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #a5b4fc;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.mf-card-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.2;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #fff 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mf-card-sub {
    font-size: 0.95rem;
    color: #cbd5e1;
    margin-top: 0.5rem;
    line-height: 1.6;
    font-weight: 400;
}

/* ── Premium Metric ── */
.mf-premium-metric {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%);
    border-left: 4px solid #6366f1;
    padding-left: 1.5rem;
    position: relative;
}

.mf-premium-metric::after {
    content: '✦';
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 1.5rem;
    color: rgba(99,102,241,0.3);
    animation: pulse 2s ease-in-out infinite;
}

/* ── Upload info box ── */
.mf-upload-info {
    background: linear-gradient(135deg, rgba(99,102,241,.1) 0%, rgba(139,92,246,.08) 100%);
    border: 1px solid rgba(99,102,241,.25);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #c7d2fe;
    font-size: .9rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(99,102,241,.1);
    animation: fadeIn 0.5s ease-out;
}

/* ── Botões Premium ── */
button[kind="primary"], .stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 16px rgba(99,102,241,.3) !important;
}

button[kind="primary"]:hover, .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,.4) !important;
}

button[kind="primary"]:active, .stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Inputs Premium ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(30,30,46,0.6) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    background: rgba(30,30,46,0.8) !important;
}

/* ── Tabs Premium ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(30,30,46,0.4);
    padding: 0.5rem;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white !important;
}

/* ── Expander Premium ── */
.streamlit-expanderHeader {
    background: rgba(30,30,46,0.6) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(30,30,46,0.8) !important;
    border-color: rgba(99,102,241,0.4) !important;
}

/* ── Status Container Premium ── */
.stStatus {
    background: rgba(30,30,46,0.6) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
}

/* ── Footer Premium ── */
.mf-footer {
    text-align: center;
    padding: 2.5rem 1rem;
    margin-top: 4rem;
    border-top: 1px solid rgba(99,102,241,.15);
    color: #64748b;
    font-size: .9rem;
    animation: fadeIn 0.8s ease-out;
}

.mf-footer strong {
    color: #6366f1;
    font-weight: 700;
}

.mf-footer a {
    color: #818cf8;
    text-decoration: none;
    transition: color 0.3s ease;
}

.mf-footer a:hover {
    color: #a5b4fc;
}
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
