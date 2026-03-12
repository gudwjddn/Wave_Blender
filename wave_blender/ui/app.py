import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from wave_blender.audio_loader import (
    load_audio,
    normalize_audio,
    SUPPORTED_FORMATS,
)
from wave_blender.wave_synth import (
    WaveformType,
    WAVEFORM_LABELS,
    generate_waveform,
    waveform_to_audio_segment,
)
from wave_blender.mixer import mix_audio
from wave_blender.exporter import export_audio


FREQ_MIN = 1
FREQ_MAX = 20000
OFFSET_MIN = -24
OFFSET_MAX = 0


class WaveBlenderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Wave Blender")
        self.root.resizable(False, False)

        self.audio = None
        self.audio_dbfs = None

        self._build_ui()
        self._set_status("준비됨")

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 5}

        # --- File section ---
        file_frame = ttk.LabelFrame(self.root, text="음원 파일", padding=10)
        file_frame.pack(fill="x", **pad)

        ttk.Label(file_frame, text="파일:").grid(row=0, column=0, sticky="w")
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, width=45, state="readonly").grid(
            row=0, column=1, padx=(5, 5)
        )
        ttk.Button(file_frame, text="찾아보기...", command=self._on_browse).grid(
            row=0, column=2
        )

        self.file_status_var = tk.StringVar(value="")
        ttk.Label(file_frame, textvariable=self.file_status_var, foreground="gray").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(5, 0)
        )

        # --- Wave settings section ---
        wave_frame = ttk.LabelFrame(self.root, text="파형 설정", padding=10)
        wave_frame.pack(fill="x", **pad)

        ttk.Label(wave_frame, text="파형 종류:").grid(row=0, column=0, sticky="w")
        self.wave_labels = [WAVEFORM_LABELS[wt] for wt in WaveformType]
        self.wave_types = list(WaveformType)
        self.wave_var = tk.StringVar(value=self.wave_labels[0])
        wave_combo = ttk.Combobox(
            wave_frame,
            textvariable=self.wave_var,
            values=self.wave_labels,
            state="readonly",
            width=15,
        )
        wave_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))

        ttk.Label(wave_frame, text="주파수:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        freq_row = ttk.Frame(wave_frame)
        freq_row.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(5, 0))
        self.freq_var = tk.StringVar(value="440")
        ttk.Entry(freq_row, textvariable=self.freq_var, width=10).pack(side="left")
        ttk.Label(freq_row, text=f"Hz  ({FREQ_MIN}~{FREQ_MAX:,})").pack(side="left", padx=(5, 0))

        ttk.Label(wave_frame, text="볼륨 오프셋:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        offset_row = ttk.Frame(wave_frame)
        offset_row.grid(row=2, column=1, sticky="w", padx=(5, 0), pady=(5, 0))
        self.offset_var = tk.StringVar(value="-6")
        ttk.Entry(offset_row, textvariable=self.offset_var, width=10).pack(side="left")
        ttk.Label(offset_row, text=f"dB  ({OFFSET_MIN}~{OFFSET_MAX})").pack(
            side="left", padx=(5, 0)
        )

        # --- Export section ---
        export_frame = ttk.Frame(self.root, padding=10)
        export_frame.pack(fill="x", padx=10)

        fmt_row = ttk.Frame(export_frame)
        fmt_row.pack(fill="x", pady=(0, 5))
        ttk.Label(fmt_row, text="출력 포맷:").pack(side="left")
        self.format_var = tk.StringVar(value="MP3")
        ttk.Combobox(
            fmt_row,
            textvariable=self.format_var,
            values=["WAV", "MP3", "MP4"],
            state="readonly",
            width=8,
        ).pack(side="left", padx=(5, 0))

        self.export_btn = ttk.Button(
            export_frame, text="음원 내보내기...", command=self._on_export
        )
        self.export_btn.pack(fill="x", ipady=5)

        # --- Status bar ---
        status_frame = ttk.Frame(self.root, padding=(10, 5))
        status_frame.pack(fill="x")
        self.status_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.status_var, foreground="gray").pack(
            side="left"
        )

    def _set_status(self, msg: str) -> None:
        self.status_var.set(f"상태: {msg}")

    def _on_browse(self) -> None:
        ext_list = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_FORMATS))
        filepath = filedialog.askopenfilename(
            title="음원 파일 선택",
            filetypes=[("오디오 파일", ext_list), ("모든 파일", "*.*")],
        )
        if not filepath:
            return

        self._set_status("로딩 중...")
        self.root.update_idletasks()

        try:
            audio = load_audio(filepath)
            normalized, dbfs = normalize_audio(audio)
        except ValueError as e:
            messagebox.showerror("오류", str(e))
            self._set_status("준비됨")
            return

        self.audio = normalized
        self.audio_dbfs = dbfs
        self.file_var.set(os.path.basename(filepath))

        if dbfs == float("-inf"):
            self.file_status_var.set("무음 파일입니다")
        else:
            self.file_status_var.set(f"로드 완료 & {dbfs:.1f} dBFS로 정규화됨")

        self._set_status("준비됨")

    def _on_export(self) -> None:
        if self.audio is None:
            messagebox.showwarning("경고", "먼저 음원 파일을 선택하세요.")
            return

        # Validate frequency
        try:
            freq = float(self.freq_var.get())
            if not (FREQ_MIN <= freq <= FREQ_MAX):
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", f"주파수는 {FREQ_MIN}~{FREQ_MAX:,} Hz 범위여야 합니다.")
            return

        # Validate offset
        try:
            offset = float(self.offset_var.get())
            if not (OFFSET_MIN <= offset <= OFFSET_MAX):
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", f"볼륨 오프셋은 {OFFSET_MIN}~{OFFSET_MAX} dB 범위여야 합니다.")
            return

        # Get waveform type
        label_idx = self.wave_labels.index(self.wave_var.get())
        wave_type = self.wave_types[label_idx]

        # Get output format and path
        fmt = self.format_var.get().lower()
        output_path = filedialog.asksaveasfilename(
            title="내보낼 파일 저장",
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} 파일", f"*.{fmt}")],
        )
        if not output_path:
            return

        # Disable export button during processing
        self.export_btn.config(state="disabled")
        self._set_status("처리 중...")
        self.root.update_idletasks()

        def process():
            try:
                samples = generate_waveform(
                    kind=wave_type,
                    frequency_hz=freq,
                    duration_ms=len(self.audio),
                    sample_rate=self.audio.frame_rate,
                )
                wave_seg = waveform_to_audio_segment(
                    samples=samples,
                    sample_rate=self.audio.frame_rate,
                    channels=self.audio.channels,
                    sample_width=self.audio.sample_width,
                )
                mixed = mix_audio(
                    base_audio=self.audio,
                    wave_audio=wave_seg,
                    offset_db=offset,
                )
                result_path = export_audio(mixed, output_path, format=fmt)
                self.root.after(0, lambda: self._export_done(result_path))
            except Exception as e:
                self.root.after(0, lambda: self._export_error(str(e)))

        threading.Thread(target=process, daemon=True).start()

    def _export_done(self, path: str) -> None:
        self.export_btn.config(state="normal")
        self._set_status("내보내기 완료!")
        messagebox.showinfo("완료", f"파일이 저장되었습니다:\n{path}")

    def _export_error(self, msg: str) -> None:
        self.export_btn.config(state="normal")
        self._set_status("준비됨")
        messagebox.showerror("내보내기 오류", msg)
