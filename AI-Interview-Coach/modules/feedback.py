from typing import Dict, List


def generate_feedback(payload: Dict) -> List[str]:
    feedback = []
    relevance = payload.get("relevance", {}).get("relevance_score", 0.0)
    voice = payload.get("voice", {}).get("voice_confidence_score", 0.0)
    eye = payload.get("eye_contact", {}).get("eye_contact_score", 0.0)
    posture = payload.get("posture", {}).get("posture_score", 0.0)
    emotion = payload.get("emotion", {}).get("dominant_emotion", "neutral")
    speech_clarity = payload.get("voice", {}).get("speech_clarity_score", 0.0)

    if relevance < 65:
        feedback.append("Improve answer relevance by structuring points using problem-action-result.")
    if voice < 65:
        feedback.append("Speak confidently with stable volume and moderate pace.")
    if eye < 65:
        feedback.append("Maintain eye contact by keeping your gaze centered toward the camera.")
    if posture < 65:
        feedback.append("Sit straight and keep your shoulders level to improve body language.")
    if speech_clarity < 65:
        feedback.append("Reduce long pauses and articulate key words clearly.")
    if emotion in {"sad", "angry", "fear"}:
        feedback.append("Keep a calm, positive expression to project confidence.")

    if not feedback:
        feedback.append("Great job. Keep practicing with varied questions for even stronger performance.")

    return feedback
