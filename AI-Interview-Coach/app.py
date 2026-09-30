import html
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from modules.answer_analysis import score_answer_relevance
from modules.database import fetch_history, init_db, save_interview
from modules.emotion_detection import detect_emotion_from_image
from modules.eye_contact import analyze_eye_contact
from modules.feedback import generate_feedback
from modules.posture_analysis import analyze_posture
from modules.questions import (
    generate_followup_question,
    get_ideal_answer,
    get_random_question,
)
from modules.report_generator import generate_pdf_report
from modules.scoring import compute_final_score
from modules.speech_to_text import save_uploaded_file, transcribe_audio
from modules.voice_analysis import analyze_voice_confidence
from ui.charts import plot_gauge_score, plot_history_trend, plot_radar
from ui.components import (
    feature_grid,
    feedback_section,
    hero_banner,
    optional_timer_fragment,
    recording_badge,
    split_feedback_buckets,
)
from ui.styles import inject_theme_css


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "history.db"
ALLOWED_AUDIO_EXT = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac"}

LANGUAGE_MAP = {"English": "en", "Hindi": "hi", "Punjabi": "pa"}

NAV_LABELS: List[Tuple[str, str]] = [
    ("🏠 Home", "home"),
    ("🎯 Start Interview", "role"),
    ("🎙 Live Session", "interview"),
    ("📊 Results", "results"),
    ("📁 History", "history"),
    ("⚙ Settings", "settings"),
]

# Bound to st.sidebar radio; Streamlit forbids assigning this after the widget renders in the same run.
SIDEBAR_RADIO_KEY = "sidebar_nav_radio"


def _nav_sidebar_labels_ids() -> Tuple[List[str], List[str]]:
    labels = [lbl for lbl, _ in NAV_LABELS]
    ids = [pid for _, pid in NAV_LABELS]
    return labels, ids


def _reset_sidebar_radio_widget() -> None:
    """Drop persisted radio value so the next run uses `index` derived from `page` (programmatic nav)."""
    st.session_state.pop(SIDEBAR_RADIO_KEY, None)


def navigate_to(page_id: str) -> None:
    """Change route; clear sidebar widget state so it cannot fight `page` after `st.rerun()`."""
    st.session_state["page"] = page_id
    _reset_sidebar_radio_widget()
    st.rerun()

ROLE_CARDS: List[Tuple[str, str, str, str]] = [
    ("HR Interview", "HR", "🧑‍💼", "Culture, motivation, and behavioral prompts."),
    ("Software Engineer", "Software Engineer", "💻", "Systems design, quality, and delivery depth."),
    ("Data Analyst", "Data Analyst", "📈", "Metrics, experiments, and stakeholder storytelling."),
    ("Custom Role", "Custom", "✨", "Bring your own title — tailored general prompts."),
]

LEGACY_PAGE_MAP = {
    "Home": "home",
    "Role Selection": "role",
    "Interview Screen": "interview",
    "Results Dashboard": "results",
    "History Page": "history",
}


def _migrate_page_state() -> None:
    p = st.session_state.get("page", "home")
    if p in LEGACY_PAGE_MAP:
        st.session_state["page"] = LEGACY_PAGE_MAP[p]


def _init_state() -> None:
    defaults = {
        "page": "home",
        "selected_role": None,
        "language": "English",
        "question": None,
        "transcript": "",
        "analysis_result": None,
        "final_score": None,
        "feedback": [],
        "report_payload": None,
        "last_error": None,
        "ui_theme": "dark",
        "role_pick_internal": "HR Interview",
        "interview_timer_started": None,
        "reset_timer": False,
        "camera_pref": "System default (browser managed)",
        "mic_pref": "System default (browser managed)",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    _migrate_page_state()


def _apply_page_config() -> None:
    st.set_page_config(
        page_title="AI Interview Coach",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def _capture_audio_ui() -> Optional[str]:
    st.markdown("##### Audio input")
    st.caption(
        "Windows tip: if analysis fails with “cannot find the file specified”, install ffmpeg "
        "from https://ffmpeg.org/download.html and add it to PATH, or upload a standard PCM .wav file."
    )
    source = st.radio("Choose input mode", ["Microphone Recording", "Upload Audio File"], horizontal=True)
    audio_ready = False
    saved_path: Optional[str] = None

    if source == "Microphone Recording" and hasattr(st, "audio_input"):
        recorded = st.audio_input("Record your answer")
        if recorded is not None:
            name = getattr(recorded, "name", "") or "recording.wav"
            suffix = Path(name).suffix.lower()
            if suffix not in ALLOWED_AUDIO_EXT:
                suffix = ".wav"
            out = DATA_DIR / f"session_audio{suffix}"
            save_uploaded_file(recorded, str(out))
            saved_path = str(out)
            audio_ready = True
            st.success("Audio captured — ready to analyze.")
    else:
        uploaded = st.file_uploader("Upload `.wav` or `.mp3`", type=["wav", "mp3"])
        if uploaded is not None:
            name = getattr(uploaded, "name", "") or "upload.wav"
            suffix = Path(name).suffix.lower()
            if suffix not in ALLOWED_AUDIO_EXT:
                suffix = ".wav"
            out = DATA_DIR / f"session_audio{suffix}"
            save_uploaded_file(uploaded, str(out))
            saved_path = str(out)
            audio_ready = True
            st.success("Audio uploaded — ready to analyze.")

    if not audio_ready:
        st.info("Provide audio to enable analysis.")
        return None

    return saved_path


def _render_sidebar_nav() -> str:
    labels, ids = _nav_sidebar_labels_ids()
    current = st.session_state.get("page", "home")
    if current not in ids:
        current = "home"
        st.session_state["page"] = current
        _reset_sidebar_radio_widget()
    index = ids.index(current)
    with st.sidebar:
        st.markdown("### AI Interview Coach")
        st.caption("Premium mock interview studio")
        st.divider()
        choice_label = st.radio(
            "Navigate",
            options=labels,
            index=index,
            key=SIDEBAR_RADIO_KEY,
            label_visibility="collapsed",
        )
        selected_id = ids[labels.index(choice_label)]
        st.session_state["page"] = selected_id
        st.divider()
        st.caption("Tip: use wide layout for the best dashboard experience.")
    return selected_id


def _home_page() -> None:
    hero_banner("AI Interview Coach", "Your Personal AI-Powered Interview Mentor")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    cta1, cta2, _ = st.columns([1, 1, 2])
    with cta1:
        if st.button("Start Interview", type="primary", use_container_width=True):
            navigate_to("role")
    with cta2:
        if st.button("View History", use_container_width=True):
            navigate_to("history")

    st.markdown("#### Capabilities")
    feature_grid(
        [
            ("🎤", "Speech Analysis", "Transcription plus clarity and confidence scoring."),
            ("😊", "Emotion Detection", "Understand how your expression reads on camera."),
            ("👁", "Eye Contact", "Track gaze alignment toward the interviewer."),
            ("🧍", "Posture Analysis", "Surface body-language cues that impact trust."),
            ("📄", "Smart Report", "Export a polished PDF to share or revisit."),
        ]
    )


def _role_selection_page() -> None:
    st.markdown("## Choose your track")
    st.caption("Select a role card — each path uses tailored question banks.")

    cols = st.columns(4)
    for idx, (internal, short, icon, desc) in enumerate(ROLE_CARDS):
        with cols[idx]:
            selected = st.session_state.get("role_pick_internal") == internal
            border = "2px solid #06b6d4" if selected else "1px solid var(--app-border)"
            glow = "rgba(6,182,212,0.25)" if selected else "transparent"
            st.markdown(
                f"""
                <div class="saas-card saas-role-card" style="border: {border}; box-shadow: 0 0 0 1px {glow}; min-height: 160px;">
                    <div style="font-size:1.75rem;">{icon}</div>
                    <div style="font-weight:800; font-size:1.1rem; margin:6px 0;">{short}</div>
                    <div class="saas-muted" style="font-size:0.9rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select", key=f"role_select_{idx}", use_container_width=True):
                st.session_state["role_pick_internal"] = internal
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("##### Interview language")
    lang_options = list(LANGUAGE_MAP.keys())
    lang_index = lang_options.index(st.session_state["language"]) if st.session_state["language"] in lang_options else 0
    language = st.selectbox("Language", lang_options, index=lang_index, key="lang_global", label_visibility="collapsed")
    st.session_state["language"] = language

    custom_role = ""
    if st.session_state.get("role_pick_internal") == "Custom Role":
        custom_role = st.text_input("Describe your custom role", placeholder="e.g., Product Manager", key="custom_role_field")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Continue to interview workspace", type="primary", use_container_width=True):
        internal = st.session_state.get("role_pick_internal", "HR Interview")
        resolved = custom_role.strip() if internal == "Custom Role" else internal
        if internal == "Custom Role" and not custom_role.strip():
            st.warning("Add a custom role name to continue.")
            return
        st.session_state["selected_role"] = resolved if internal == "Custom Role" else internal
        st.session_state["language"] = language
        st.session_state["question"] = get_random_question(role_name=st.session_state["selected_role"])
        st.session_state["analysis_result"] = None
        st.session_state["final_score"] = None
        st.session_state["feedback"] = []
        st.session_state["report_payload"] = None
        st.session_state["transcript"] = ""
        st.session_state["reset_timer"] = True
        navigate_to("interview")


def _run_pipeline_with_progress(
    *,
    audio_path: str,
    camera_image,
    role: str,
    language: str,
    question: str,
) -> None:
    progress = st.progress(0)
    status = st.empty()
    status.markdown('<p class="shimmer" style="color:#e2e8f0;font-weight:600;">Analyzing speech...</p>', unsafe_allow_html=True)

    try:
        transcript_data = transcribe_audio(
            audio_path=audio_path,
            language_code=LANGUAGE_MAP.get(language, "en"),
        )
        transcript = transcript_data.get("transcript", "").strip()
        st.session_state["transcript"] = transcript
        progress.progress(28)

        status.markdown('<p class="shimmer" style="color:#e2e8f0;font-weight:600;">Calculating confidence...</p>', unsafe_allow_html=True)
        ideal_answer = get_ideal_answer(question)
        relevance_data = score_answer_relevance(
            question=question,
            user_answer=transcript,
            ideal_answer=ideal_answer,
        )
        voice_data = analyze_voice_confidence(audio_path=audio_path, transcript=transcript)
        progress.progress(55)

        status.markdown('<p class="shimmer" style="color:#e2e8f0;font-weight:600;">Detecting emotion...</p>', unsafe_allow_html=True)
        visual_emotion = {"dominant_emotion": "neutral", "emotion_score": 50.0}
        eye_data = {"eye_contact_score": 50.0}
        posture_data = {"posture_label": "Needs Improvement", "posture_score": 50.0}
        if camera_image is not None:
            import cv2
            import numpy as np

            file_bytes = np.asarray(bytearray(camera_image.getvalue()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            visual_emotion = detect_emotion_from_image(frame)
            eye_data = analyze_eye_contact(frame)
            posture_data = analyze_posture(frame)
        progress.progress(78)

        status.markdown('<p class="shimmer" style="color:#e2e8f0;font-weight:600;">Generating report...</p>', unsafe_allow_html=True)
        all_scores = compute_final_score(
            relevance_score=relevance_data.get("relevance_score", 0.0),
            voice_score=voice_data.get("voice_confidence_score", 0.0),
            dominant_emotion=visual_emotion.get("dominant_emotion", "neutral"),
            eye_contact_score=eye_data.get("eye_contact_score", 0.0),
            posture_score=posture_data.get("posture_score", 0.0),
            speech_clarity_score=voice_data.get("speech_clarity_score", 0.0),
        )

        payload = {
            "role": role,
            "language": language,
            "question": question,
            "ideal_answer": ideal_answer,
            "transcript": transcript,
            "relevance": relevance_data,
            "voice": voice_data,
            "emotion": visual_emotion,
            "eye_contact": eye_data,
            "posture": posture_data,
            "scores": all_scores,
            "followup_question": generate_followup_question(transcript, role, language),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state["analysis_result"] = payload
        st.session_state["final_score"] = all_scores.get("final_score", 0.0)
        st.session_state["feedback"] = generate_feedback(payload)
        st.session_state["report_payload"] = generate_pdf_report(payload, st.session_state["feedback"])
        save_interview(
            db_path=str(DB_PATH),
            role=role,
            score=float(st.session_state["final_score"]),
            emotion=visual_emotion.get("dominant_emotion", "neutral"),
            question=question,
            transcript=transcript,
        )
        progress.progress(100)
        status.markdown('<p style="color:#5eead4;font-weight:600;">Analysis complete — opening results.</p>', unsafe_allow_html=True)
        time.sleep(0.35)
        navigate_to("results")
    except Exception as exc:
        st.session_state["last_error"] = str(exc)
        progress.progress(100)
        status.empty()
        st.error(f"Analysis failed: {exc}")


def _interview_screen_page() -> None:
    role = st.session_state.get("selected_role")
    language = st.session_state.get("language", "English")
    question = st.session_state.get("question")

    if st.session_state.pop("reset_timer", False):
        st.session_state["interview_timer_started"] = time.time()

    if not role:
        st.warning("Pick a role to unlock the interview workspace.")
        if st.button("Go to role selection", type="primary"):
            navigate_to("role")
        return

    if not question:
        question = get_random_question(role_name=role)
        st.session_state["question"] = question

    st.markdown(
        f"""
        <div class="saas-card" style="margin-bottom: 14px;">
            <div style="font-size:0.85rem; color: var(--app-muted);">Active role</div>
            <div style="font-size:1.35rem; font-weight:800;">{role}</div>
            <div class="saas-muted">Language · {language}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("##### Question")
        st.markdown(f'<div class="saas-card">{html.escape(question)}</div>', unsafe_allow_html=True)
        optional_timer_fragment(st.session_state.get("interview_timer_started"))
        st.markdown("##### Session transcript")
        st.text_area(
            "Transcript",
            value=st.session_state.get("transcript", ""),
            height=140,
            disabled=True,
            label_visibility="collapsed",
            help="Transcript fills in automatically after analysis.",
        )
        st.caption("Transcript updates automatically after analysis — keep answers concise and structured.")
        audio_path = _capture_audio_ui()

    with right:
        st.markdown("##### Webcam preview")
        camera_image = st.camera_input("Live preview", label_visibility="collapsed")
        st.session_state["interview_cam"] = camera_image
        audio_ready = audio_path is not None
        recording_badge(
            active=audio_ready,
            label="Audio captured — ready to analyze" if audio_ready else "Waiting for audio input",
        )
        st.caption("Blinking indicator highlights when audio is ready for scoring.")

    with left:
        cam_snapshot = st.session_state.get("interview_cam")
        if st.button("Analyze interview", type="primary", use_container_width=True, disabled=audio_path is None):
            _run_pipeline_with_progress(
                audio_path=audio_path or "",
                camera_image=cam_snapshot,
                role=role,
                language=language,
                question=question,
            )


def _results_dashboard_page() -> None:
    result: Dict = st.session_state.get("analysis_result") or {}
    if not result:
        st.markdown("## Results dashboard")
        st.info("Complete an interview analysis to unlock your analytics cockpit.")
        if st.button("Start interview", type="primary"):
            navigate_to("role")
        return

    scores = result.get("scores", {})
    relevance = float(result.get("relevance", {}).get("relevance_score", 0.0))
    voice = float(result.get("voice", {}).get("voice_confidence_score", 0.0))
    eye = float(result.get("eye_contact", {}).get("eye_contact_score", 0.0))
    posture_score = float(result.get("posture", {}).get("posture_score", 0.0))
    emotion_label = result.get("emotion", {}).get("dominant_emotion", "neutral")
    final_score = float(scores.get("final_score", 0.0))

    st.markdown("## Results dashboard")
    st.caption("Multimodal scoring, visual analytics, and export-ready reporting.")

    top_left, top_right = st.columns([1.1, 1.0])
    with top_left:
        plot_gauge_score(final_score, title="Final score")
    with top_right:
        st.markdown("##### Score breakdown")
        st.caption(f"Answer relevance · {relevance:.1f}%")
        st.progress(min(max(relevance / 100, 0.0), 1.0))
        st.caption(f"Voice confidence · {voice:.1f}%")
        st.progress(min(max(voice / 100, 0.0), 1.0))
        st.caption(f"Eye contact · {eye:.1f}%")
        st.progress(min(max(eye / 100, 0.0), 1.0))

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Answer relevance", f"{relevance:.1f}%")
    with m2:
        st.metric("Voice confidence", f"{voice:.1f}%")
    with m3:
        st.metric("Emotion", emotion_label.title())
    with m4:
        st.metric("Eye contact", f"{eye:.1f}%")
    with m5:
        st.metric("Posture", result.get("posture", {}).get("posture_label", "—"))

    plot_radar(scores)

    strengths, improvements, warnings = split_feedback_buckets(
        st.session_state.get("feedback", []),
        emotion_label,
        final_score,
        relevance,
        voice,
        eye,
        posture_score,
    )
    feedback_section(strengths, improvements, warnings)

    st.markdown("##### Transcript")
    st.text_area("Transcript output", value=result.get("transcript", ""), height=160, disabled=True, label_visibility="collapsed")

    if result.get("followup_question"):
        st.info(f"AI follow-up: {result.get('followup_question')}")

    report_bytes = st.session_state.get("report_payload")
    if report_bytes:
        st.download_button(
            label="⬇ Download PDF report",
            data=report_bytes,
            file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Start new round", use_container_width=True):
            st.session_state["question"] = get_random_question(role_name=st.session_state.get("selected_role"))
            st.session_state["reset_timer"] = True
            navigate_to("interview")
    with b2:
        if st.button("View history", use_container_width=True):
            navigate_to("history")
    with b3:
        if st.button("Return home", use_container_width=True):
            navigate_to("home")


def _history_page() -> None:
    st.markdown("## Interview history")
    history_df = fetch_history(str(DB_PATH))
    if history_df.empty:
        st.info("No interviews yet — your timeline will light up after your first session.")
        return

    work = history_df.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    roles = sorted(work["role"].dropna().unique().tolist())
    f1, f2, f3 = st.columns([1.1, 1.1, 1.4])
    with f1:
        pick_roles = st.multiselect("Filter by role", options=roles, default=roles)
    with f2:
        dmin = work["date"].min().date() if work["date"].notna().any() else datetime.now().date()
        dmax = work["date"].max().date() if work["date"].notna().any() else datetime.now().date()
        dr = st.date_input("Date range", value=(dmin, dmax))
    with f3:
        st.caption("Filters apply instantly to the table and trend visualization.")

    filtered = work[work["role"].isin(pick_roles)] if pick_roles else work
    if isinstance(dr, tuple) and len(dr) == 2:
        start, end = dr
        filtered = filtered[(filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)]

    display_cols = ["date", "role", "score", "emotion", "question"]
    st.dataframe(
        filtered[display_cols].sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    plot_history_trend(filtered)

    st.caption("Use insights from the trend line to schedule focused practice on weak dimensions.")


def _settings_page() -> None:
    st.markdown("## Settings")
    st.caption("Tune presentation, language, and device preferences.")

    c1, c2 = st.columns(2)
    with c1:
        theme = st.selectbox("Theme", options=["dark", "light"], index=0 if st.session_state.get("ui_theme", "dark") == "dark" else 1)
        st.session_state["ui_theme"] = theme
    with c2:
        lang_options = list(LANGUAGE_MAP.keys())
        lang_index = lang_options.index(st.session_state["language"]) if st.session_state["language"] in lang_options else 0
        language = st.selectbox("Interview language", lang_options, index=lang_index, key="lang_global")
        st.session_state["language"] = language

    d1, d2 = st.columns(2)
    with d1:
        cam_opts = [
            "System default (browser managed)",
            "Prefer front camera",
            "Prefer rear / external camera",
        ]
        cur_cam = st.session_state.get("camera_pref", cam_opts[0])
        cam_index = cam_opts.index(cur_cam) if cur_cam in cam_opts else 0
        cam = st.selectbox("Camera", options=cam_opts, index=cam_index)
        st.session_state["camera_pref"] = cam
        st.info("Streamlit routes video through your browser. Use the browser permission chip to swap physical devices.")
    with d2:
        mic_opts = [
            "System default (browser managed)",
            "Prefer built-in mic",
            "Prefer external mic",
        ]
        cur_mic = st.session_state.get("mic_pref", mic_opts[0])
        mic_index = mic_opts.index(cur_mic) if cur_mic in mic_opts else 0
        mic = st.selectbox("Microphone", options=mic_opts, index=mic_index)
        st.session_state["mic_pref"] = mic
        st.info("Microphone routing is handled by the operating system for `st.audio_input` recordings.")

    st.markdown("##### Experience")
    st.write("Animations use lightweight CSS shimmer effects to keep installs lean (no extra animation servers).")


def main() -> None:
    _apply_page_config()
    _init_state()
    inject_theme_css(str(st.session_state.get("ui_theme", "dark")))
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db(str(DB_PATH))

    if st.session_state.get("last_error"):
        st.error(st.session_state["last_error"])
        if st.button("Clear error"):
            st.session_state["last_error"] = None
            st.rerun()

    selected = _render_sidebar_nav()

    if selected == "home":
        _home_page()
    elif selected == "role":
        _role_selection_page()
    elif selected == "interview":
        _interview_screen_page()
    elif selected == "results":
        _results_dashboard_page()
    elif selected == "history":
        _history_page()
    else:
        _settings_page()


if __name__ == "__main__":
    main()
