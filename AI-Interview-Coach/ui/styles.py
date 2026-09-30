from __future__ import annotations

import streamlit as st

THEMES = {
    "dark": {
        "bg": "#0f172a",
        "card": "#1e293b",
        "card_glass": "rgba(30, 41, 59, 0.72)",
        "accent": "#06b6d4",
        "accent_soft": "rgba(6, 182, 212, 0.15)",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "border": "rgba(148, 163, 184, 0.18)",
        "shadow": "0 18px 45px rgba(2, 6, 23, 0.55)",
    },
    "light": {
        "bg": "#f1f5f9",
        "card": "#ffffff",
        "card_glass": "rgba(255, 255, 255, 0.78)",
        "accent": "#0891b2",
        "accent_soft": "rgba(8, 145, 178, 0.12)",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "rgba(15, 23, 42, 0.08)",
        "shadow": "0 14px 40px rgba(15, 23, 42, 0.12)",
    },
}


def inject_theme_css(theme: str) -> None:
    t = THEMES.get(theme, THEMES["dark"])
    light_sidebar_patch = ""
    if theme == "light":
        light_sidebar_patch = """
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
                border-right: 1px solid rgba(15,23,42,0.08) !important;
            }
            [data-testid="stSidebar"] * {
                color: #0f172a !important;
            }
        """
    st.markdown(
        f"""
        <style>
            :root {{
                --app-bg: {t["bg"]};
                --app-card: {t["card"]};
                --app-card-glass: {t["card_glass"]};
                --app-accent: {t["accent"]};
                --app-accent-soft: {t["accent_soft"]};
                --app-text: {t["text"]};
                --app-muted: {t["muted"]};
                --app-border: {t["border"]};
                --app-shadow: {t["shadow"]};
            }}
            .stApp {{
                background: radial-gradient(1200px 600px at 10% -10%, rgba(6,182,212,0.12), transparent 55%),
                            radial-gradient(900px 500px at 100% 0%, rgba(99,102,241,0.10), transparent 50%),
                            var(--app-bg) !important;
                color: var(--app-text);
            }}
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header[data-testid="stHeader"] {{
                background: transparent;
            }}
            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.88) 100%) !important;
                border-right: 1px solid var(--app-border);
            }}
            [data-testid="stSidebar"] * {{
                color: #e2e8f0 !important;
            }}
            [data-testid="stSidebar"] .stMarkdown a {{
                color: #67e8f9 !important;
            }}
            div[data-testid="stVerticalBlock"] > div:has(> div > [data-testid="stMarkdown"]) .stMarkdown p,
            div[data-testid="stVerticalBlock"] > div:has(> div > [data-testid="stMarkdown"]) .stMarkdown li {{
                color: var(--app-text);
            }}
            h1, h2, h3, h4 {{
                color: var(--app-text) !important;
                letter-spacing: -0.02em;
            }}
            .stMetric label {{
                color: var(--app-muted) !important;
            }}
            .stMetric [data-testid="stMetricValue"] {{
                color: var(--app-text) !important;
            }}
            div[data-baseweb="radio"] label,
            div[data-baseweb="select"] label {{
                color: var(--app-text);
            }}
            .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {{
                background: var(--app-card-glass) !important;
                color: var(--app-text) !important;
                border: 1px solid var(--app-border) !important;
                border-radius: 12px !important;
            }}
            .stDownloadButton button, .stButton > button {{
                border-radius: 12px !important;
                border: 1px solid rgba(6,182,212,0.45) !important;
                background: linear-gradient(135deg, rgba(6,182,212,0.35), rgba(99,102,241,0.22)) !important;
                color: var(--app-text) !important;
                font-weight: 600 !important;
                box-shadow: var(--app-shadow);
                transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
            }}
            .stDownloadButton button:hover, .stButton > button:hover {{
                transform: translateY(-1px);
                filter: brightness(1.06);
                box-shadow: 0 22px 50px rgba(6, 182, 212, 0.25);
            }}
            .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, #06b6d4, #6366f1) !important;
                border: none !important;
                color: #0b1220 !important;
            }}
            .saas-card {{
                background: var(--app-card-glass);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border: 1px solid var(--app-border);
                border-radius: 18px;
                padding: 1.25rem 1.35rem;
                box-shadow: var(--app-shadow);
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            }}
            .saas-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 24px 55px rgba(6, 182, 212, 0.18);
                border-color: rgba(6, 182, 212, 0.35);
            }}
            .saas-hero {{
                background: linear-gradient(135deg, rgba(6,182,212,0.18), rgba(99,102,241,0.14));
                border: 1px solid var(--app-border);
                border-radius: 22px;
                padding: 2.25rem 2rem;
                box-shadow: var(--app-shadow);
                backdrop-filter: blur(16px);
            }}
            .saas-hero h1 {{
                font-size: clamp(2rem, 4vw, 2.75rem);
                margin-bottom: 0.35rem;
            }}
            .saas-muted {{
                color: var(--app-muted);
                font-size: 1.05rem;
            }}
            .saas-feature-icon {{
                font-size: 1.6rem;
                margin-bottom: 0.35rem;
            }}
            .saas-role-card {{
                cursor: pointer;
                user-select: none;
            }}
            .rec-dot {{
                width: 10px;
                height: 10px;
                border-radius: 999px;
                background: #ef4444;
                display: inline-block;
                margin-right: 8px;
                vertical-align: middle;
                animation: pulse-dot 1.1s ease-in-out infinite;
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.55);
            }}
            @keyframes pulse-dot {{
                0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.55); opacity: 1; }}
                70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); opacity: 0.85; }}
                100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); opacity: 1; }}
            }}
            .shimmer {{
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
                background-size: 200% 100%;
                animation: shimmer 1.4s linear infinite;
            }}
            @keyframes shimmer {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
            div[data-testid="stExpander"] {{
                background: var(--app-card-glass);
                border: 1px solid var(--app-border);
                border-radius: 14px;
            }}
            {light_sidebar_patch}
        </style>
        """,
        unsafe_allow_html=True,
    )
