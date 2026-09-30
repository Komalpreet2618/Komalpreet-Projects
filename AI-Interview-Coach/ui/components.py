from __future__ import annotations

import html
from typing import Iterable, List, Optional

import streamlit as st


def hero_banner(title: str, subtitle: str) -> None:
    safe_title = html.escape(title)
    safe_sub = html.escape(subtitle)
    st.markdown(
        f"""
        <div class="saas-hero">
            <h1>{safe_title}</h1>
            <p class="saas-muted" style="margin:0;">{safe_sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_grid(items: List[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (icon, name, desc) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="saas-card" style="min-height: 140px;">
                    <div class="saas-feature-icon">{html.escape(icon)}</div>
                    <div style="font-weight:700; margin-bottom:6px; color: var(--app-text);">{html.escape(name)}</div>
                    <div class="saas-muted" style="font-size:0.92rem;">{html.escape(desc)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def metric_card(title: str, body_html: str) -> None:
    st.markdown(
        f"""
        <div class="saas-card" style="margin-bottom: 12px;">
            <div style="font-size:0.85rem; color: var(--app-muted); margin-bottom:6px;">{html.escape(title)}</div>
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def feedback_section(strengths: Iterable[str], improvements: Iterable[str], warnings: Iterable[str]) -> None:
    s_list = list(strengths)
    i_list = list(improvements)
    w_list = list(warnings)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### Strengths")
        if not s_list:
            st.caption("No strengths listed yet.")
        for line in s_list:
            st.markdown(
                f'<div class="saas-card" style="border-left: 4px solid #22c55e;">{html.escape(line)}</div>',
                unsafe_allow_html=True,
            )
    with c2:
        st.markdown("##### Improvements")
        if not i_list:
            st.caption("Looking good — few improvements.")
        for line in i_list:
            st.markdown(
                f'<div class="saas-card" style="border-left: 4px solid #eab308;">{html.escape(line)}</div>',
                unsafe_allow_html=True,
            )
    with c3:
        st.markdown("##### Warnings")
        if not w_list:
            st.caption("No critical warnings.")
        for line in w_list:
            st.markdown(
                f'<div class="saas-card" style="border-left: 4px solid #ef4444;">{html.escape(line)}</div>',
                unsafe_allow_html=True,
            )


def recording_badge(active: bool, label: str) -> None:
    dot = '<span class="rec-dot"></span>' if active else '<span style="display:inline-block;width:10px;height:10px;border-radius:999px;background:#64748b;margin-right:8px;vertical-align:middle;"></span>'
    st.markdown(
        f'<div class="saas-card" style="display:flex;align-items:center;gap:8px;">{dot}<span>{html.escape(label)}</span></div>',
        unsafe_allow_html=True,
    )


def split_feedback_buckets(
    feedback_lines: List[str],
    emotion: str,
    final_score: float,
    relevance: float,
    voice: float,
    eye: float,
    posture: float,
) -> tuple[List[str], List[str], List[str]]:
    strengths: List[str] = []
    if relevance >= 75:
        strengths.append("Answer relevance is strong — keep linking examples to outcomes.")
    if voice >= 75:
        strengths.append("Vocal delivery sounds confident and steady.")
    if eye >= 75:
        strengths.append("Eye contact toward the camera reads professional.")
    if posture >= 75:
        strengths.append("Posture supports an engaged, credible presence.")
    if (emotion or "").lower() in {"happy", "neutral", "surprise"} and final_score >= 70:
        strengths.append("Overall presence aligns with a positive interview signal.")

    improvements = list(feedback_lines)

    warnings: List[str] = []
    if final_score < 50:
        warnings.append("Overall score is low — focus on one skill per practice round.")
    em = (emotion or "").lower()
    if em in {"sad", "angry", "fear"}:
        warnings.append("Facial tone may read as stressed — pause, breathe, and soften expression.")
    if relevance < 45:
        warnings.append("Answer relevance is critically low — clarify the question before diving in.")
    if eye < 40:
        warnings.append("Eye contact is very low — anchor your gaze near the webcam lens.")

    return strengths, improvements, warnings


def optional_timer_fragment(start_ts: Optional[float]) -> None:
    if start_ts is None:
        return
    frag = getattr(st, "fragment", None)
    if frag is None:
        import time

        elapsed = max(0.0, time.time() - start_ts)
        m, s = int(elapsed // 60), int(elapsed % 60)
        st.metric("Session timer", f"{m:02d}:{s:02d}")
        return

    @frag(run_every=1.0)
    def _tick() -> None:
        import time

        elapsed = max(0.0, time.time() - start_ts)
        m, s = int(elapsed // 60), int(elapsed % 60)
        st.metric("Session timer", f"{m:02d}:{s:02d}")

    _tick()
