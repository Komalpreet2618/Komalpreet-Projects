from typing import Dict

from deepface import DeepFace


def detect_emotion_from_image(image_bgr) -> Dict:
    try:
        result = DeepFace.analyze(img_path=image_bgr, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list):
            result = result[0]
        emotion_map = result.get("emotion", {}) or {}
        dominant = str(result.get("dominant_emotion", "neutral")).lower()
        emotion_score = float(emotion_map.get(dominant, 0.0))
        return {
            "dominant_emotion": dominant,
            "emotion_probabilities": emotion_map,
            "emotion_score": max(0.0, min(100.0, emotion_score)),
        }
    except Exception:
        return {"dominant_emotion": "neutral", "emotion_probabilities": {}, "emotion_score": 50.0}
