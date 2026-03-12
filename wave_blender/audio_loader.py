import os
import subprocess
from pydub import AudioSegment

SUPPORTED_FORMATS_NO_FFMPEG = {".wav"}
SUPPORTED_FORMATS_WITH_FFMPEG = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".wma"}
TARGET_DBFS = -20.0
PEAK_CEILING_DBFS = -1.0


def is_ffmpeg_available() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return True
    except FileNotFoundError:
        return False


def get_supported_formats() -> set[str]:
    if is_ffmpeg_available():
        return SUPPORTED_FORMATS_WITH_FFMPEG
    return SUPPORTED_FORMATS_NO_FFMPEG


def load_audio(filepath: str) -> AudioSegment:
    ext = os.path.splitext(filepath)[1].lower()
    supported = get_supported_formats()

    if ext not in supported:
        if ext in SUPPORTED_FORMATS_WITH_FFMPEG:
            raise ValueError(
                f"'{ext}' 포맷을 사용하려면 ffmpeg가 필요합니다.\n"
                f"현재 지원 포맷: {', '.join(sorted(supported))}"
            )
        raise ValueError(
            f"지원하지 않는 파일 포맷입니다: {ext}\n"
            f"지원 포맷: {', '.join(sorted(supported))}"
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
