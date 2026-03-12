import tkinter as tk
import imageio_ffmpeg
from pydub import AudioSegment

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

from wave_blender.ui.app import WaveBlenderApp


def main() -> None:
    root = tk.Tk()
    root.geometry("520x370")
    WaveBlenderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
