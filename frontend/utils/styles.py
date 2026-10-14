import streamlit as st


def style_plotly_figure(figure):
    return figure.update_layout(
        paper_bgcolor="#e5e7eb",
        plot_bgcolor="#e5e7eb",
    )


def inject_global_styles():

    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True
    )

    st.markdown("""
                <style>
                

    /* ── HIDE SIDEBAR ─────────────────────────────────── */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"],
    section[data-testid="stSidebar"] { display: none !important; }

    
    /* ── ROOT TOKENS ──────────────────────────────────── */
    :root {
        --bg:          #f4f7fb;
        --bg-alt:      #f8fafc;
        --bg-card:     #ffffff;
        --bg-glass:    rgba(255,255,255,0.72);
        --bg-input:    #f8fafc;
        --navy:        #0f2547;
        --navy-lt:     #1e3a5f;
        --navy-md:     #163263;
        --gold:        #f59e0b;
        --gold-dk:     #d97706;
        --gold-glow:   rgba(245,158,11,0.18);
        --green:       #15803d;
        --green-lt:    #166534;
        --saffron:     #FF9933;
        --white-ind:   #ffffff;
        --india-green: #138808;
        --ashoka-blue: #000080;
        --text-h:      #0f2547;
        --text-b:      #1e293b;
        --text-s:      #475569;
        --text-m:      #94a3b8;
        --border:      #e8edf4;
        --border-md:   #d1dae8;
        --shadow-sm:   0 2px 12px rgba(15,37,71,0.07);
        --shadow-md:   0 6px 28px rgba(15,37,71,0.11);
        --shadow-lg:   0 16px 48px rgba(15,37,71,0.14);
    }

    /* ── BASE + SUBTLE RADIAL GRADIENT BACKGROUND ─────── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .main {
        background-color: var(--bg) !important;
        background-image:
            radial-gradient(ellipse 80% 60% at 10% 0%,  rgba(15,37,71,0.045) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 90% 100%, rgba(245,158,11,0.06) 0%, transparent 55%),
            radial-gradient(ellipse 50% 50% at 50% 50%,  rgba(19,136,8,0.025) 0%, transparent 70%) !important;
        color: var(--text-b) !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding: 1.8rem 2.5rem !important; max-width: 1400px; }

    /* ── DECORATIVE CORNER BLOBS ──────────────────────── */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed; top: -120px; left: -120px;
        width: 380px; height: 380px;
        background: radial-gradient(circle, rgba(15,37,71,0.07) 0%, transparent 65%);
        pointer-events: none; z-index: 0;
    }
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed; bottom: -100px; right: -100px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(245,158,11,0.09) 0%, transparent 65%);
        pointer-events: none; z-index: 0;
    }

    /* ── EQUAL HEIGHT COLUMNS ─────────────────────────── */
    [data-testid="stHorizontalBlock"] { align-items: stretch !important; }
    [data-testid="column"] { display: flex !important; flex-direction: column !important; }
    [data-testid="column"] > div[data-testid="stVerticalBlock"] {
        flex: 1 !important; display: flex !important; flex-direction: column !important;
    }

    /* ── TYPOGRAPHY ───────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Rajdhani', sans-serif !important;
        color: var(--text-h) !important;
    }
    p, li { color: var(--text-b); }
    .stMarkdown p:not(.hero-subtitle){
        color:var(--text-b);
    }
    /* ===========================
    HERO TEXT FIX
    =========================== */

    .hero-wrap .hero-sub,
    .hero-wrap .hero-sub p,
    .stMarkdown .hero-wrap .hero-sub,
    .stMarkdown .hero-wrap .hero-sub p {
        color: #ffffff !important;
    }
    [data-testid="stCaption"] { color: var(--text-m) !important; }
    label[data-testid="stWidgetLabel"] > div > p { color: var(--text-s) !important; }

    /* ── SECTION HEADER DECORATION — TRICOLOUR STRIPE ─── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.6rem;
    }
    .section-header h3 {
        margin: 0 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.6rem !important;
        color: var(--navy) !important;
    }
    .tricolour-bar {
        display: inline-flex;
        flex-direction: column;
        gap: 2px;
        width: 5px;
        height: 38px;
        border-radius: 4px;
        overflow: hidden;
        flex-shrink: 0;
    }
    .tricolour-bar span:nth-child(1) { flex:1; background: var(--saffron); }
    .tricolour-bar span:nth-child(2) { flex:1; background: var(--white-ind); border: 1px solid #ddd; }
    .tricolour-bar span:nth-child(3) { flex:1; background: var(--india-green); }

    /* ── ICON GLOW CIRCLE ─────────────────────────────── */
    .icon-glow {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: #eef6ff;
        border: 1.5px solid rgba(15,37,71,0.1);
        box-shadow:
            0 0 0 6px rgba(15,37,71,0.04),
            0 0 18px rgba(15,37,71,0.08);
        margin-bottom: 1rem;
        font-size: 1.7rem;
        transition: box-shadow 0.3s;
    }
    .icon-glow:hover {
        box-shadow:
            0 0 0 8px rgba(245,158,11,0.08),
            0 0 24px rgba(245,158,11,0.2);
    }
    .icon-glow.gold-glow {
        background: #fff8ec;
        box-shadow:
            0 0 0 6px rgba(245,158,11,0.07),
            0 0 18px rgba(245,158,11,0.15);
    }
    .icon-glow.green-glow {
        background: #ecfdf5;
        box-shadow:
            0 0 0 6px rgba(19,136,8,0.06),
            0 0 18px rgba(19,136,8,0.12);
    }

    /* ── BUTTONS ──────────────────────────────────────── */
    .stButton > button {
        background: #0E7A00 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: .95rem !important;
        font-weight: 600 !important;
        padding: .55rem 1.4rem !important;
        transition: background 0.2s !important;
    }
    .stButton > button span,
    .stButton > button p,
    .stButton > button div { color: #ffffff !important; }
    .stButton > button:hover { background: #095c00 !important; }

    .secondary-btn-container .stButton > button {
        background: rgba(255,255,255,0.85) !important;
        color: var(--navy) !important;
        border: 1.5px solid var(--border-md) !important;
        backdrop-filter: blur(4px) !important;
    }
    .secondary-btn-container .stButton > button span,
    .secondary-btn-container .stButton > button p {
        color: var(--navy) !important;
        background: transparent !important;
    }
    .secondary-btn-container .stButton > button:hover {
        background: var(--bg-alt) !important;
    }

    .citizen-btn-container .stButton > button {
        background: var(--green) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        padding: .7rem 1.6rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(21,128,61,0.25) !important;
    }
    .citizen-btn-container .stButton > button:hover {
        background: var(--green-lt) !important;
        box-shadow: 0 6px 20px rgba(21,128,61,0.35) !important;
    }

    .official-btn-container .stButton > button {
        background: var(--navy) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        padding: .7rem 1.6rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(15,37,71,0.2) !important;
    }
    .official-btn-container .stButton > button:hover {
        background: var(--navy-md) !important;
    }

    .submit-btn-container .stButton > button {
        background: var(--green) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        padding: .75rem 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(21,128,61,0.25) !important;
    }

    .track-btn-container .stButton > button {
        background: var(--navy) !important;
        color: #ffffff !important;
        border: 1.5px solid var(--navy) !important;
    }

    [data-testid="stDownloadButton"] > button {
        background: var(--navy) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(15,37,71,0.18) !important;
    }
    [data-testid="stDownloadButton"] > button span,
    [data-testid="stDownloadButton"] > button p { color: #ffffff !important; }

    /* ── INPUTS ───────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea  > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: var(--bg-glass) !important;
        color: var(--text-b) !important;
        border: 1.5px solid var(--border-md) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(4px) !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea  > div > div > textarea::placeholder { color: var(--text-m) !important; }
    .stTextInput > div > div > input:focus,
    .stTextArea  > div > div > textarea:focus {
        border-color: var(--navy) !important;
        box-shadow: 0 0 0 3px rgba(15,37,71,0.1), 0 2px 8px rgba(15,37,71,0.08) !important;
    }
    .stSelectbox > div > div > div { color: var(--text-b) !important; }

    /* ── METRICS ──────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-glass) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: var(--shadow-sm) !important;
        backdrop-filter: blur(6px) !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--navy) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-s) !important;
        font-size: .75rem !important;
        text-transform: uppercase;
        letter-spacing: .07em;
    }

    /* ── DATAFRAME ────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stDataFrame"] thead th {
        background: var(--bg-alt) !important;
        color: var(--text-h) !important;
    }
    [data-testid="stDataFrame"] tbody td { color: var(--text-b) !important; }

    /* ── EXPANDERS ────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: var(--bg-glass) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        margin-bottom: .6rem !important;
        backdrop-filter: blur(4px) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stExpander"] summary { color: var(--text-h) !important; font-weight: 600 !important; }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p { color: var(--text-b) !important; }

    /* ── ALERTS ───────────────────────────────────────── */
    [data-testid="stAlert"] { border-radius: 10px !important; }
    hr { border-color: var(--border) !important; opacity: 1 !important; }

    /* ── SOFT BOTTOM FADE ─────────────────────────────── */
    .soft-bottom-fade {
        position: relative;
        padding-bottom: 3rem;
    }
    .soft-bottom-fade::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 120px;
        background: linear-gradient(to bottom, transparent, var(--bg));
        pointer-events: none;
    }

    /* ── ALTERNATING SECTION BACKGROUNDS ─────────────── */
    .section-white { background: #ffffff; padding: 2rem 0; border-radius: 16px; margin-bottom: 1.5rem; }
    .section-alt   { background: #f8fafc; padding: 2rem 0; border-radius: 16px; margin-bottom: 1.5rem; }

    /* ── HERO BANNER ──────────────────────────────────── */
    .hero-wrap {
        background: linear-gradient(135deg, #0d1b3e 0%, #0f2547 45%, #1a3a2e 100%);
        border: 2px solid var(--gold);
        border-radius: 20px;
        padding: 3.2rem 3rem;
        margin-bottom: 2.2rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
    }
    .hero-wrap::before {
        content: '';
        position: absolute; top: -100px; right: -60px;
        width: 380px; height: 380px;
        background: radial-gradient(circle, rgba(21,128,61,0.28) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-wrap::after {
        content: '';
        position: absolute; bottom: -60px; left: 40%;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(245,158,11,0.14) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-tag {
        font-size: .7rem; letter-spacing: .22em; text-transform: uppercase;
        color: var(--gold); margin-bottom: .7rem; font-weight: 700;
    }
    .hero-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 3rem; font-weight: 700;
        line-height: 1.1; color: #ffffff; margin-bottom: .9rem;
    }
    .hero-title span { color: var(--gold); }
    .hero-sub { color: #cbd5e1; font-size: .95rem; max-width: 560px; line-height: 1.7; }
    .hero-sub p { color: #cbd5e1 !important; }

    /* Gold accent line below hero heading */
    .hero-accent-line {
        display: block;
        width: 60px; height: 3px;
        background: linear-gradient(90deg, var(--gold), transparent);
        border-radius: 2px;
        margin: .5rem 0 1rem 0;
    }

    /* ── STAT TILES ───────────────────────────────────── */
    .stat-tile {
        background: var(--bg-glass);
        border: 1.5px solid var(--border);
        border-radius: 14px;
        padding: 1.6rem 1.6rem;
        text-align: center;
        height: 100%;
        box-shadow: var(--shadow-sm);
        backdrop-filter: blur(8px);
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .stat-tile:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .stat-tile .num {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.4rem; font-weight: 700;
        color: var(--navy); line-height: 1;
    }
    .stat-tile .num.gold { color: var(--gold); }
    .stat-tile .lbl {
        font-size: .72rem; color: var(--text-s);
        letter-spacing: .08em; text-transform: uppercase; margin-top: .4rem;
    }
    /* Gold accent line under stat number */
    .stat-tile .stat-line {
        display: block;
        width: 32px; height: 2px;
        background: var(--gold);
        border-radius: 2px;
        margin: .4rem auto .2rem auto;
    }

    /* ── PORTAL CARDS — GLASSMORPHISM ─────────────────── */
    .portal-card {
        background: var(--bg-glass);
        border: 1.5px solid rgba(255,255,255,0.9);
        border-top: 4px solid var(--gold);
        border-radius: 18px;
        padding: 2.4rem 2rem 1.8rem 2rem;
        min-height: 230px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        backdrop-filter: blur(12px);
        box-shadow:
            0 4px 24px rgba(15,37,71,0.08),
            inset 0 1px 0 rgba(255,255,255,0.6);
        transition: box-shadow 0.25s, transform 0.25s;
    }
    .portal-card:hover {
        box-shadow:
            0 10px 36px rgba(15,37,71,0.13),
            inset 0 1px 0 rgba(255,255,255,0.6);
        transform: translateY(-3px);
    }
    .portal-icon { font-size: 2.4rem; color: var(--navy); margin-bottom: .8rem; }
    .portal-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.5rem; font-weight: 700;
        color: var(--navy); margin-bottom: .5rem;
    }
    .portal-desc { color: var(--text-s); font-size: .92rem; line-height: 1.6; }

    /* ── GENERIC CARD — GLASSMORPHISM ─────────────────── */
    .lk-card {
        background: var(--bg-glass);
        border: 1.5px solid rgba(255,255,255,0.85);
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.1rem;
        backdrop-filter: blur(8px);
        box-shadow:
            var(--shadow-sm),
            inset 0 1px 0 rgba(255,255,255,0.55);
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .lk-card:hover {
        box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.55);
        transform: translateY(-2px);
    }
    .lk-card h4 { color: var(--text-h) !important; }
    .lk-card p, .lk-card li { color: var(--text-b) !important; }

    /* ── COMPLAINT ID ─────────────────────────────────── */
    .complaint-id {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.2rem; font-weight: 700;
        color: var(--gold); letter-spacing: .1em;
    }

    /* ── DEMO BOX ─────────────────────────────────────── */
    .demo-box {
        border: 1.5px dashed var(--gold);
        border-radius: 10px;
        padding: 1rem 1.4rem;
        background: rgba(255,248,236,0.85);
        backdrop-filter: blur(4px);
        text-align: center;
        margin-top: 1.5rem;
        color: var(--text-b);
        font-size: .92rem;
    }
    .demo-box strong { color: var(--text-h); }
    .demo-title { color: var(--gold-dk); font-weight: 700; margin-bottom: .4rem; }

    </>""", unsafe_allow_html=True)
    