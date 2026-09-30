"""
Load mono 16 kHz float32 audio without calling Whisper's ffmpeg pipeline when possible.

Whisper's default file loading always invokes `ffmpeg` as a subprocess; on Windows that
raises WinError 2 if ffmpeg is not installed on PATH. Reading WAV/PCM via soundfile or
scipy avoids that for typical recordings.
"""

from pathlib import Path

import numpy as np


TARGET_SR = 16000


def _resample_if_needed(data: np.ndarray, orig_sr: int, target_sr: int = TARGET_SR) -> np.ndarray:
    if orig_sr == target_sr:
        return data.astype(np.float32, copy=False)
    import librosa

    return librosa.resample(data.astype(np.float32), orig_sr=orig_sr, target_sr=target_sr).astype(np.float32)


def load_audio_mono_16k(path: str) -> np.ndarray:
    """
    Return mono float32 audio at 16 kHz, shape (n_samples,).

    Order: soundfile (WAV/FLAC/etc.) -> scipy WAV -> librosa (may use ffmpeg for mp3/webm).
    """
    path = str(path)
    if not Path(path).is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    # 1) soundfile (no ffmpeg for common PCM WAV)
    try:
        import soundfile as sf

        data, sr = sf.read(path, dtype="float32", always_2d=False)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        return _resample_if_needed(data, int(sr))
    except Exception:
        pass

    # 2) scipy WAV reader
    try:
        from scipy.io import wavfile

        sr, data = wavfile.read(path)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        if np.issubdtype(data.dtype, np.floating):
            audio = data.astype(np.float32)
        elif data.dtype == np.int16:
            audio = (data.astype(np.float32)) / 32768.0
        elif data.dtype == np.int32:
            audio = (data.astype(np.float32)) / 2147483648.0
        elif data.dtype == np.uint8:
            audio = (data.astype(np.float32) - 128.0) / 128.0
        else:
            audio = data.astype(np.float32)
        return _resample_if_needed(audio, int(sr))
    except Exception:
        pass

    # 3) librosa (mp3 / odd containers often need ffmpeg on the system)
    try:
        import librosa

        y, sr = librosa.load(path, sr=TARGET_SR, mono=True)
        return y.astype(np.float32)
    except OSError as exc:
        win = getattr(exc, "winerror", None)
        if win == 2 or "WinError 2" in str(exc):
            raise OSError(
                "Could not load audio. For MP3/WebM or if loading fails, install ffmpeg "
                "from https://ffmpeg.org/download.html and add it to your PATH, "
                "or upload a standard PCM .wav file."
            ) from exc
        raise
