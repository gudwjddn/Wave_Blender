from enum import Enum

import numpy as np
from scipy import signal
from pydub import AudioSegment


class WaveformType(Enum):
    SINE = "sine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"


WAVEFORM_LABELS = {
    WaveformType.SINE: "사인파",
    WaveformType.SQUARE: "사각파",
    WaveformType.SAWTOOTH: "톱니파",
    WaveformType.TRIANGLE: "삼각파",
}


def generate_waveform(
    kind: WaveformType,
    frequency_hz: float,
    duration_ms: int,
    sample_rate: int = 44100,
) -> np.ndarray:
    num_samples = int(sample_rate * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms / 1000.0, num_samples, endpoint=False)
    phase = 2 * np.pi * frequency_hz * t

    if kind == WaveformType.SINE:
        samples = np.sin(phase)
    elif kind == WaveformType.SQUARE:
        samples = signal.square(phase)
    elif kind == WaveformType.SAWTOOTH:
        samples = signal.sawtooth(phase)
    elif kind == WaveformType.TRIANGLE:
        samples = signal.sawtooth(phase, width=0.5)
    else:
        raise ValueError(f"지원하지 않는 파형: {kind}")

    return samples


def generate_binaural_waveform(
    kind: WaveformType,
    base_hz: float,
    beat_hz: float,
    duration_ms: int,
    sample_rate: int = 44100,
) -> np.ndarray:
    """L=base_hz, R=base_hz+beat_hz 스테레오 배열 반환. shape (N, 2)."""
    L = generate_waveform(kind, base_hz, duration_ms, sample_rate)
    R = generate_waveform(kind, base_hz + beat_hz, duration_ms, sample_rate)
    return np.column_stack([L, R])


def waveform_to_audio_segment(
    samples: np.ndarray,
    sample_rate: int = 44100,
    channels: int = 1,
    sample_width: int = 2,
) -> AudioSegment:
    if samples.ndim == 2:
        if samples.shape[1] != 2 or channels != 2:
            raise ValueError("2D samples require shape (N, 2) and channels=2")
        clipped = np.clip(samples, -1.0, 1.0)
        raw_data = (clipped * 32767).astype(np.int16).tobytes()
        out_channels = 2
    elif samples.ndim == 1:
        clipped = np.clip(samples, -1.0, 1.0)
        int_samples = (clipped * 32767).astype(np.int16)
        if channels == 2:
            raw_data = np.column_stack([int_samples, int_samples]).tobytes()
        else:
            raw_data = int_samples.tobytes()
        out_channels = channels
    else:
        raise ValueError(f"지원하지 않는 배열 차원: {samples.ndim}")

    # Always build as int16 (sample_width=2); mixer.set_sample_width() will
    # convert to the base audio's actual sample width if needed.
    return AudioSegment(
        data=raw_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=out_channels,
    )
