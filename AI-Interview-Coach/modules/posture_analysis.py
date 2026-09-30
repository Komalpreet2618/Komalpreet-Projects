from typing import Dict

import cv2
import numpy as np

try:
    import mediapipe as mp  # type: ignore
except Exception:
    mp = None


def _build_pose():
    if mp is None or not hasattr(mp, "solutions"):
        return None
    try:
        return mp.solutions.pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    except Exception:
        return None


_pose = _build_pose()


def _xy(landmark, width, height):
    return np.array([landmark.x * width, landmark.y * height], dtype=np.float32)


def analyze_posture(image_bgr) -> Dict:
    if image_bgr is None:
        return {"posture_label": "Needs Improvement", "posture_score": 0.0}
    if _pose is None or mp is None or not hasattr(mp, "solutions"):
        return {
            "posture_label": "Needs Improvement",
            "posture_score": 50.0,
            "warning": "MediaPipe Pose unavailable in current environment.",
        }

    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    result = _pose.process(rgb)
    if not result.pose_landmarks:
        return {"posture_label": "Needs Improvement", "posture_score": 0.0}

    h, w = image_bgr.shape[:2]
    lm = result.pose_landmarks.landmark

    left_shoulder = _xy(lm[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value], w, h)
    right_shoulder = _xy(lm[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value], w, h)
    left_ear = _xy(lm[mp.solutions.pose.PoseLandmark.LEFT_EAR.value], w, h)
    right_ear = _xy(lm[mp.solutions.pose.PoseLandmark.RIGHT_EAR.value], w, h)

    shoulder_slope = abs(float(np.degrees(np.arctan2(right_shoulder[1] - left_shoulder[1], right_shoulder[0] - left_shoulder[0]))))
    ear_center = (left_ear + right_ear) / 2.0
    shoulder_center = (left_shoulder + right_shoulder) / 2.0
    head_forward = abs(float(ear_center[0] - shoulder_center[0])) / max(1.0, abs(right_shoulder[0] - left_shoulder[0]))

    score = 100.0 - min(40.0, shoulder_slope * 2.0) - min(35.0, head_forward * 120.0)
    score = max(0.0, min(100.0, score))
    label = "Good" if score >= 65 else "Needs Improvement"

    return {
        "posture_label": label,
        "posture_score": round(score, 2),
        "shoulder_slope_deg": round(shoulder_slope, 2),
        "head_tilt_ratio": round(head_forward, 4),
    }
