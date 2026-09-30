from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def plot_gauge_score(score: float, title: str = "Final Score") -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=min(max(float(score), 0.0), 100.0),
            title={"text": title, "font": {"size": 18, "color": "#e2e8f0"}},
            number={"font": {"size": 44, "color": "#f8fafc"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                "bar": {"color": "#06b6d4"},
                "bgcolor": "rgba(15,23,42,0.4)",
                "borderwidth": 1,
                "bordercolor": "rgba(148,163,184,0.35)",
                "steps": [
                    {"range": [0, 45], "color": "rgba(239,68,68,0.25)"},
                    {"range": [45, 70], "color": "rgba(234,179,8,0.22)"},
                    {"range": [70, 100], "color": "rgba(34,197,94,0.18)"},
                ],
                "threshold": {
                    "line": {"color": "#f8fafc", "width": 3},
                    "thickness": 0.8,
                    "value": float(score),
                },
            },
        )
    )
    fig.update_layout(
        height=320,
        margin=dict(l=24, r=24, t=40, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def plot_radar(scores: Dict[str, float]) -> None:
    categories: List[str] = ["Answer", "Voice", "Emotion", "Eye Contact", "Posture"]
    values = [
        float(scores.get("relevance_score", 0.0)),
        float(scores.get("voice_score", 0.0)),
        float(scores.get("emotion_score", 0.0)),
        float(scores.get("eye_contact_score", 0.0)),
        float(scores.get("posture_score", 0.0)),
    ]
    values_closed = values + [values[0]]
    cats_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=cats_closed,
            fill="toself",
            fillcolor="rgba(6,182,212,0.25)",
            line=dict(color="#06b6d4", width=2),
            name="Your session",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(15,23,42,0.35)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148,163,184,0.25)"),
            angularaxis=dict(gridcolor="rgba(148,163,184,0.25)"),
        ),
        showlegend=False,
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        title={"text": "Performance radar", "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def plot_history_trend(df: pd.DataFrame, date_col: str = "date", score_col: str = "score") -> None:
    if df.empty:
        return
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col]).sort_values(date_col)
    if work.empty:
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=work[date_col],
            y=work[score_col],
            mode="lines+markers",
            line=dict(color="#06b6d4", width=3, shape="spline"),
            marker=dict(size=8, color="#67e8f9", line=dict(color="#0e7490", width=1)),
            fill="tozeroy",
            fillcolor="rgba(6,182,212,0.12)",
        )
    )
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.25)",
        xaxis=dict(title="Date", gridcolor="rgba(148,163,184,0.2)", color="#e2e8f0"),
        yaxis=dict(title="Score", range=[0, 105], gridcolor="rgba(148,163,184,0.2)", color="#e2e8f0"),
        title={"text": "Score progression", "x": 0.5, "xanchor": "center", "font": {"color": "#e2e8f0"}},
        font={"color": "#e2e8f0"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
