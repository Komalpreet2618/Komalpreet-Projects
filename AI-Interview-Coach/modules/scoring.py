from typing import Dict


WEIGHTS = {
    "relevance": 0.30,
    "voice": 0.20,
    "emotion": 0.15,
    "eye_contact": 0.15,
    "posture": 0.10,
    "speech_clarity": 0.10,
}

EMOTION_SCORE_MAP = {
    "happy": 90.0,
    "neutral": 75.0,
    "sad": 40.0,
    "angry": 35.0,
    "fear": 45.0,
    "surprise": 70.0,
}


def _emotion_to_score(emotion: str) -> float:
    return EMOTION_SCORE_MAP.get((emotion or "neutral").lower(), 60.0)


def compute_final_score(
    relevance_score: float,
    voice_score: float,
    dominant_emotion: str,
    eye_contact_score: float,
    posture_score: float,
    speech_clarity_score: float,
) -> Dict[str, float]:
    emotion_score = _emotion_to_score(dominant_emotion)
    final_score = (
        relevance_score * WEIGHTS["relevance"]
        + voice_score * WEIGHTS["voice"]
        + emotion_score * WEIGHTS["emotion"]
        + eye_contact_score * WEIGHTS["eye_contact"]
        + posture_score * WEIGHTS["posture"]
        + speech_clarity_score * WEIGHTS["speech_clarity"]
    )

    return {
        "relevance_score": round(float(relevance_score), 2),
        "voice_score": round(float(voice_score), 2),
        "emotion_score": round(float(emotion_score), 2),
        "eye_contact_score": round(float(eye_contact_score), 2),
        "posture_score": round(float(posture_score), 2),
        "speech_clarity_score": round(float(speech_clarity_score), 2),
        "final_score": round(float(final_score), 2),
    }
