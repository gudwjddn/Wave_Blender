import os
import sys
import tkinter as tk

# Set ffmpeg path for PyInstaller bundled builds
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
    ffmpeg_path = os.path.join(bundle_dir, "ffmpeg", "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        from pydub import AudioSegment
        AudioSegment.converter = ffmpeg_path

from wave_blender.ui.app import WaveBlenderApp


def main() -> None:
    root = tk.Tk()
    root.geometry("520x370")
    WaveBlenderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
