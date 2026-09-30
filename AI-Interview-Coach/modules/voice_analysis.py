from typing import Dict

import librosa
import numpy as np

from modules.audio_io import load_audio_mono_16k


def analyze_voice_confidence(audio_path: str, transcript: str = "") -> Dict:
    try:
        y = load_audio_mono_16k(audio_path)
    except OSError:
        raise
    except Exception:
        y, _sr = librosa.load(audio_path, sr=16000, mono=True)
    sr = 16000
    if y.size == 0:
        return {
            "speaking_speed_wpm": 0.0,
            "pause_count": 0,
            "pitch_variation": 0.0,
            "energy": 0.0,
            "voice_confidence_score": 0.0,
            "speech_clarity_score": 0.0,
        }

    duration_sec = librosa.get_duration(y=y, sr=sr)
    words = len((transcript or "").split())
    speaking_speed_wpm = (words / max(duration_sec, 1e-6)) * 60.0 if words > 0 else 0.0

    frame_length = 1024
    hop_length = 256
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    energy = float(np.mean(rms))

    silence_threshold = max(0.005, float(np.percentile(rms, 25)))
    pause_count = int(np.sum(rms < silence_threshold))
    pause_count = int(pause_count / 15)

    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitch_vals = pitches[pitches > 0]
    pitch_variation = float(np.std(pitch_vals)) if pitch_vals.size > 0 else 0.0

    speed_component = 100.0 - min(abs(speaking_speed_wpm - 135.0), 135.0) * (100.0 / 135.0)
    pause_component = max(0.0, 100.0 - pause_count * 5.0)
    pitch_component = min(100.0, pitch_variation / 2.0)
    energy_component = min(100.0, energy * 1200.0)

    confidence_score = (
        speed_component * 0.35
        + pause_component * 0.25
        + pitch_component * 0.2
        + energy_component * 0.2
    )
    confidence_score = max(0.0, min(100.0, confidence_score))

    speech_clarity = (pause_component * 0.6 + energy_component * 0.4)
    speech_clarity = max(0.0, min(100.0, speech_clarity))

    return {
        "speaking_speed_wpm": round(speaking_speed_wpm, 2),
        "pause_count": int(pause_count),
        "pitch_variation": round(pitch_variation, 2),
        "energy": round(energy, 4),
        "voice_confidence_score": round(confidence_score, 2),
        "speech_clarity_score": round(speech_clarity, 2),
    }
