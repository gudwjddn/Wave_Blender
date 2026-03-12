import os
from pydub import AudioSegment

SUPPORTED_FORMATS = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".wma"}
TARGET_DBFS = -20.0
PEAK_CEILING_DBFS = -1.0


def load_audio(filepath: str) -> AudioSegment:
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"지원하지 않는 파일 포맷입니다: {ext}\n"
            f"지원 포맷: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    try:
        audio = AudioSegment.from_file(filepath)
    except Exception as e:
        raise ValueError(f"파일을 로드할 수 없습니다: {e}") from e

    return audio


def normalize_audio(
    audio: AudioSegment,
    target_dbfs: float = TARGET_DBFS,
    peak_ceiling_dbfs: float = PEAK_CEILING_DBFS,
) -> tuple[AudioSegment, float]:
    if audio.dBFS == float("-inf"):
        return audio, float("-inf")

    gain = target_dbfs - audio.dBFS
    normalized = audio.apply_gain(gain)

    if normalized.max_dBFS > peak_ceiling_dbfs:
        overshoot = normalized.max_dBFS - peak_ceiling_dbfs
        normalized = normalized.apply_gain(-overshoot)

    return normalized, normalized.dBFS
