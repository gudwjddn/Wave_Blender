import os
import subprocess
import tempfile
import imageio_ffmpeg
from pydub import AudioSegment


def export_audio(
    audio: AudioSegment,
    output_path: str,
    format: str = "wav",
    bitrate: str = "192k",
) -> str:
    try:
        if format == "mp4":
            _export_mp4(audio, output_path, bitrate)
        elif format == "mp3":
            audio.export(output_path, format=format, bitrate=bitrate)
        else:
            audio.export(output_path, format=format)
    except Exception as e:
        raise ValueError(f"파일 내보내기 실패: {e}") from e

    return os.path.abspath(output_path)


def _export_mp4(audio: AudioSegment, output_path: str, bitrate: str = "192k") -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        audio.export(tmp_path, format="wav")
        subprocess.run(
            [
                ffmpeg, "-y",
                "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30",
                "-i", tmp_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", bitrate,
                "-shortest",
                output_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
