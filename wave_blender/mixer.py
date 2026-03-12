from pydub import AudioSegment

WAVE_VOLUME_OFFSET_DB = -6.0
PEAK_CEILING_DBFS = -1.0


def mix_audio(
    base_audio: AudioSegment,
    wave_audio: AudioSegment,
    offset_db: float = WAVE_VOLUME_OFFSET_DB,
    peak_ceiling_dbfs: float = PEAK_CEILING_DBFS,
) -> AudioSegment:
    # 1. Match wave duration to base (loop or trim)
    base_len = len(base_audio)
    wave_len = len(wave_audio)

    if wave_len < base_len:
        repeats = (base_len // wave_len) + 1
        wave_audio = wave_audio * repeats
    wave_audio = wave_audio[:base_len]

    # 2. Match audio parameters
    wave_audio = wave_audio.set_frame_rate(base_audio.frame_rate)
    wave_audio = wave_audio.set_channels(base_audio.channels)
    wave_audio = wave_audio.set_sample_width(base_audio.sample_width)

    # 3. Set wave volume to base_dBFS + offset_db
    if wave_audio.dBFS != float("-inf") and base_audio.dBFS != float("-inf"):
        target_wave_dbfs = base_audio.dBFS + offset_db
        gain = target_wave_dbfs - wave_audio.dBFS
        wave_audio = wave_audio.apply_gain(gain)

    # 4. Overlay
    mixed = base_audio.overlay(wave_audio)

    # 5. Prevent clipping
    if mixed.max_dBFS > peak_ceiling_dbfs:
        overshoot = mixed.max_dBFS - peak_ceiling_dbfs
        mixed = mixed.apply_gain(-overshoot)

    return mixed
