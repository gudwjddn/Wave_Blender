import os
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import winsound

from pydub import AudioSegment

from wave_blender.audio_loader import (
    load_audio,
    normalize_audio,
    SUPPORTED_FORMATS,
    TARGET_DBFS,
)
from wave_blender.wave_synth import (
    WaveformType,
    WAVEFORM_LABELS,
    generate_waveform,
    generate_binaural_waveform,
    waveform_to_audio_segment,
)
from wave_blender.mixer import mix_audio
from wave_blender.exporter import export_audio


FREQ_MIN = 1
FREQ_MAX = 20000
OFFSET_MIN = -24
OFFSET_MAX = 12


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

        # Fade row
        ttk.Label(wave_frame, text="Fade In:").grid(row=3, column=0, sticky="w", pady=(5, 0))
        fade_row = ttk.Frame(wave_frame)
        fade_row.grid(row=3, column=1, sticky="w", padx=(5, 0), pady=(5, 0))
        self.fade_in_var = tk.StringVar(value="0")
        ttk.Entry(fade_row, textvariable=self.fade_in_var, width=7).pack(side="left")
        ttk.Label(fade_row, text="ms").pack(side="left", padx=(3, 15))
        ttk.Label(fade_row, text="Fade Out:").pack(side="left")
        self.fade_out_var = tk.StringVar(value="0")
        ttk.Entry(fade_row, textvariable=self.fade_out_var, width=7).pack(side="left", padx=(5, 0))
        ttk.Label(fade_row, text="ms").pack(side="left", padx=(3, 0))

        # Binaural row
        binaural_row = ttk.Frame(wave_frame)
        binaural_row.grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        self.binaural_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            binaural_row,
            text="바이노럴 비트",
            variable=self.binaural_var,
            command=self._on_binaural_toggle,
        ).pack(side="left")
        ttk.Label(binaural_row, text="비트 주파수:").pack(side="left", padx=(15, 0))
        self.beat_hz_var = tk.StringVar(value="10")
        self.beat_hz_entry = ttk.Entry(binaural_row, textvariable=self.beat_hz_var, width=7)
        self.beat_hz_entry.pack(side="left", padx=(5, 0))
        ttk.Label(binaural_row, text="Hz").pack(side="left", padx=(3, 0))
        self.beat_hz_entry.config(state="disabled")

        self.test_btn = ttk.Button(
            wave_frame, text="▶ 테스트 재생 (5초)", command=self._on_test
        )
        self.test_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0))

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

    def _on_binaural_toggle(self) -> None:
        state = "normal" if self.binaural_var.get() else "disabled"
        self.beat_hz_entry.config(state=state)

    def _parse_wave_settings(self, clip_length_ms: int):
        """주파수, offset, fade, binaural 검증. 성공 시 tuple 반환, 실패 시 None."""
        try:
            freq = float(self.freq_var.get())
            if not (FREQ_MIN <= freq <= FREQ_MAX):
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", f"주파수는 {FREQ_MIN}~{FREQ_MAX:,} Hz 범위여야 합니다.")
            return None

        try:
            offset = float(self.offset_var.get())
            if not (OFFSET_MIN <= offset <= OFFSET_MAX):
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", f"볼륨 오프셋은 {OFFSET_MIN}~{OFFSET_MAX} dB 범위여야 합니다.")
            return None

        try:
            fade_in_ms = int(self.fade_in_var.get())
            fade_out_ms = int(self.fade_out_var.get())
            if fade_in_ms < 0 or fade_out_ms < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("오류", "Fade In/Out은 0 이상의 정수(ms)여야 합니다.")
            return None

        if fade_in_ms + fade_out_ms > clip_length_ms:
            messagebox.showerror(
                "오류",
                f"Fade In + Fade Out({fade_in_ms + fade_out_ms} ms)이 "
                f"클립 길이({clip_length_ms} ms)를 초과합니다.",
            )
            return None

        binaural = self.binaural_var.get()
        beat_hz = 0.0
        if binaural:
            try:
                beat_hz = float(self.beat_hz_var.get())
                if beat_hz <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("오류", "비트 주파수는 0보다 큰 값이어야 합니다.")
                return None
            if freq + beat_hz > FREQ_MAX:
                messagebox.showerror(
                    "오류",
                    f"기준 주파수 + 비트 주파수({freq + beat_hz:.1f} Hz)가 "
                    f"최대값({FREQ_MAX:,} Hz)을 초과합니다.",
                )
                return None

        return freq, offset, fade_in_ms, fade_out_ms, binaural, beat_hz

    def _build_wave_audio(
        self,
        duration_ms: int,
        sample_rate: int,
        channels: int,
        sample_width: int,
        wave_type: WaveformType,
        freq: float,
        binaural: bool,
        beat_hz: float,
    ) -> AudioSegment:
        if binaural:
            samples = generate_binaural_waveform(wave_type, freq, beat_hz, duration_ms, sample_rate)
            return waveform_to_audio_segment(samples, sample_rate, 2, sample_width)
        else:
            samples = generate_waveform(wave_type, freq, duration_ms, sample_rate)
            return waveform_to_audio_segment(samples, sample_rate, channels, sample_width)

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

    def _on_test(self) -> None:
        parsed = self._parse_wave_settings(clip_length_ms=5000)
        if parsed is None:
            return
        freq, offset, fade_in_ms, fade_out_ms, binaural, beat_hz = parsed

        label_idx = self.wave_labels.index(self.wave_var.get())
        wave_type = self.wave_types[label_idx]

        self._test_stop_event = threading.Event()
        self._test_stop_event.clear()
        self.test_btn.config(text="■ 정지", command=self._on_stop_test)
        self._set_status("테스트 재생 중...")

        def run():
            tmp_path = None
            try:
                silent = AudioSegment.silent(duration=5000, frame_rate=44100)
                silent = silent.set_channels(2).set_sample_width(2)

                wave_seg = self._build_wave_audio(
                    len(silent), silent.frame_rate, silent.channels, silent.sample_width,
                    wave_type, freq, binaural, beat_hz,
                )

                # 파일 없이 테스트 재생 시 TARGET_DBFS 기준으로 파형 볼륨 조정
                target_wave_dbfs = TARGET_DBFS + offset
                if wave_seg.dBFS != float("-inf"):
                    wave_seg = wave_seg.apply_gain(target_wave_dbfs - wave_seg.dBFS)

                mixed = mix_audio(
                    silent, wave_seg,
                    offset_db=0,
                    fade_in_ms=fade_in_ms,
                    fade_out_ms=fade_out_ms,
                )
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                mixed.export(tmp_path, format="wav")
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                self._test_stop_event.wait(timeout=5.0)
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("오류", str(e)))
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                self.root.after(0, self._test_done)

        threading.Thread(target=run, daemon=True).start()

    def _on_stop_test(self) -> None:
        self._test_stop_event.set()

    def _test_done(self) -> None:
        self.test_btn.config(text="▶ 테스트 재생 (5초)", command=self._on_test, state="normal")
        self._set_status("테스트 재생 완료")

    def _on_export(self) -> None:
        if self.audio is None:
            messagebox.showwarning("경고", "먼저 음원 파일을 선택하세요.")
            return

        parsed = self._parse_wave_settings(clip_length_ms=len(self.audio))
        if parsed is None:
            return
        freq, offset, fade_in_ms, fade_out_ms, binaural, beat_hz = parsed

        label_idx = self.wave_labels.index(self.wave_var.get())
        wave_type = self.wave_types[label_idx]

        fmt = self.format_var.get().lower()
        base_name = os.path.splitext(self.file_var.get())[0] or "untitled"
        offset_str = f"{offset:+.0f}dB"
        bin_suffix = f"_bin{beat_hz:.0f}Hz" if binaural else ""
        default_name = f"{base_name}_{wave_type.value}_{int(freq)}Hz_{offset_str}{bin_suffix}"

        output_path = filedialog.asksaveasfilename(
            title="내보낼 파일 저장",
            initialfile=default_name,
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} 파일", f"*.{fmt}")],
        )
        if not output_path:
            return

        self.export_btn.config(state="disabled")
        self._set_status("처리 중...")
        self.root.update_idletasks()

        def process():
            try:
                base_audio = self.audio.set_channels(2) if binaural else self.audio

                wave_seg = self._build_wave_audio(
                    len(base_audio), base_audio.frame_rate, base_audio.channels,
                    base_audio.sample_width, wave_type, freq, binaural, beat_hz,
                )
                mixed = mix_audio(
                    base_audio=base_audio,
                    wave_audio=wave_seg,
                    offset_db=offset,
                    fade_in_ms=fade_in_ms,
                    fade_out_ms=fade_out_ms,
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
