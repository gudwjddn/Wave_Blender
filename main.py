import os
import sys
import tkinter as tk
import imageio_ffmpeg
from pydub import AudioSegment

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

from wave_blender.ui.app import WaveBlenderApp


def _get_icon_path() -> str | None:
    if getattr(sys, "frozen", False):
        path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
    else:
        path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    return path if os.path.exists(path) else None


def main() -> None:
    root = tk.Tk()
    root.geometry("520x370")
    icon = _get_icon_path()
    if icon:
        root.iconbitmap(icon)
    WaveBlenderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
