import os
from pydub import AudioSegment


def export_audio(
    audio: AudioSegment,
    output_path: str,
    format: str = "wav",
    bitrate: str = "192k",
) -> str:
    try:
        if format == "mp3":
            audio.export(output_path, format=format, bitrate=bitrate)
        else:
            audio.export(output_path, format=format)
    except Exception as e:
        raise ValueError(f"파일 내보내기 실패: {e}") from e

    return os.path.abspath(output_path)
