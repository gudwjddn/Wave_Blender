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


def waveform_to_audio_segment(
    samples: np.ndarray,
    sample_rate: int = 44100,
    channels: int = 1,
    sample_width: int = 2,
) -> AudioSegment:
    int_samples = (samples * 32767).astype(np.int16)

    if channels == 2:
        stereo = np.column_stack([int_samples, int_samples])
        raw_data = stereo.tobytes()
    else:
        raw_data = int_samples.tobytes()

    return AudioSegment(
        data=raw_data,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels,
    )
