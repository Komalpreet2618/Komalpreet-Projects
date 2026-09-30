from typing import Dict

import cv2
import numpy as np

try:
    import mediapipe as mp  # type: ignore
except Exception:
    mp = None


def _build_face_mesh():
    if mp is None or not hasattr(mp, "solutions"):
        return None
    try:
        return mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )
    except Exception:
        return None


_face_mesh = _build_face_mesh()


def _landmark_to_xy(landmark, width: int, height: int):
    return np.array([landmark.x * width, landmark.y * height], dtype=np.float32)


def analyze_eye_contact(image_bgr) -> Dict:
    if image_bgr is None:
        return {"eye_contact_score": 0.0, "look_direction": "unknown", "head_tilt_deg": 0.0}
    if _face_mesh is None:
        return {
            "eye_contact_score": 50.0,
            "look_direction": "unavailable",
            "head_tilt_deg": 0.0,
            "warning": "MediaPipe Face Mesh unavailable in current environment.",
        }

    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    result = _face_mesh.process(rgb)
    if not result.multi_face_landmarks:
        return {"eye_contact_score": 0.0, "look_direction": "no_face", "head_tilt_deg": 0.0}

    h, w = image_bgr.shape[:2]
    lm = result.multi_face_landmarks[0].landmark

    left_eye = _landmark_to_xy(lm[33], w, h)
    right_eye = _landmark_to_xy(lm[263], w, h)
    nose = _landmark_to_xy(lm[1], w, h)
    left_cheek = _landmark_to_xy(lm[234], w, h)
    right_cheek = _landmark_to_xy(lm[454], w, h)

    eye_mid = (left_eye + right_eye) / 2.0
    face_mid_x = (left_cheek[0] + right_cheek[0]) / 2.0
    face_width = max(1.0, abs(right_cheek[0] - left_cheek[0]))
    horizontal_offset = abs(nose[0] - face_mid_x) / face_width
    center_offset = abs(eye_mid[0] - face_mid_x) / face_width

    dx = float(right_eye[0] - left_eye[0])
    dy = float(right_eye[1] - left_eye[1])
    head_tilt_deg = float(np.degrees(np.arctan2(dy, dx)))

    penalty = (horizontal_offset * 60.0) + (center_offset * 40.0) + min(abs(head_tilt_deg), 20) * 1.0
    score = max(0.0, min(100.0, 100.0 - penalty))

    if horizontal_offset < 0.07 and center_offset < 0.08:
        direction = "center"
    elif nose[0] < face_mid_x:
        direction = "right"
    else:
        direction = "left"

    return {
        "eye_contact_score": round(score, 2),
        "look_direction": direction,
        "head_tilt_deg": round(head_tilt_deg, 2),
    }
