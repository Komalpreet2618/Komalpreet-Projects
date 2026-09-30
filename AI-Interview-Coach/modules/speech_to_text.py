from functools import lru_cache
from pathlib import Path
from typing import Dict, Union

import numpy as np
import whisper

from modules.audio_io import load_audio_mono_16k


@lru_cache(maxsize=1)
def _load_whisper_model():
    return whisper.load_model("base")


def save_uploaded_file(uploaded_file, target_path: str) -> None:
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "wb") as handle:
        handle.write(uploaded_file.getvalue())


def transcribe_audio(audio_path: str, language_code: str = "en") -> Dict:
    """
    Transcribe audio. Prefer loading as a numpy array so Whisper does not spawn ffmpeg
    (avoids WinError 2 on Windows when ffmpeg is missing for typical WAV input).
    """
    model = _load_whisper_model()
    audio: Union[str, np.ndarray] = audio_path
    try:
        audio = load_audio_mono_16k(audio_path)
    except OSError:
        raise
    except Exception:
        # Fall back to Whisper's loader (requires ffmpeg for many formats)
        audio = audio_path

    result = model.transcribe(audio, language=language_code, fp16=False)
    transcript = result.get("text", "").strip()
    return {
        "transcript": transcript,
        "language": result.get("language", language_code),
        "segments": result.get("segments", []),
    }
