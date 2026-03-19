# Wave Blender

보유 음원 파일에 합성 파형(사인파, 사각파, 톱니파, 삼각파)을 오버레이하여 export하는 Windows 데스크톱 앱.

## 주요 기능

- **음원 자동 정규화**: 파일마다 다른 볼륨을 -20 dBFS로 자동 통일
- **파형 오버레이**: Sine / Square / Sawtooth / Triangle 파형 선택
- **주파수 설정**: 1 ~ 20,000 Hz 자유 입력
- **볼륨 오프셋**: 파형 볼륨을 원본 대비 dB 단위로 조절 (-24 ~ +12 dB, 기본값 -6 dB)
- **테스트 재생**: 음원 파일 없이 현재 파형 설정을 5초간 미리 청취 (즉시 정지 가능)
- **Fade In / Fade Out**: 최종 결과물 시작/끝에 페이드 적용 (s 단위)
- **바이노럴 비트**: L/R 채널 파형 종류·주파수 독립 설정으로 분리 생성 (헤드폰 권장)
- **클리핑 방지**: 믹싱 후 peak -1 dBFS 초과 시 자동 gain 감소
- **WAV / MP3 / MP4 export** (ffmpeg 별도 설치 불필요)
  - MP4: 검은 화면(1280×720) + 오디오 트랙

## 실행 방법 (Python)

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 실행
python main.py
```

> Python 3.10 이상 필요. Python 3.13+ 사용 시 `audioop-lts`가 자동으로 설치됩니다.

## 실행 방법 (.exe)

`dist/WaveBlender.exe` 파일을 직접 실행합니다. Python 설치 불필요.

## .exe 빌드

```bash
scripts\build.bat
```

- `assets/icon.png` 또는 루트의 `icon.png`가 있으면 자동으로 앱 아이콘으로 적용됩니다.
- 빌드 결과물: `dist/WaveBlender.exe`

## 사용법

1. **찾아보기** 버튼으로 음원 파일 선택 (.wav, .mp3, .ogg, .flac 등)
2. 파형 종류, 주파수(Hz), 볼륨 오프셋(dB) 설정
3. *(선택)* Fade In / Fade Out 시간 입력 (s, 기본값 0)
4. *(선택)* **바이노럴 비트** 체크 → L/R 채널 파형 종류·주파수 각각 설정 (헤드폰 착용 권장)
   - mono 원본도 자동으로 stereo로 변환하여 저장
5. *(선택)* **▶ 테스트 재생** 버튼으로 파형 미리 듣기 — **■ 정지**로 즉시 중단 가능
6. 출력 포맷 선택 (WAV / MP3 / MP4)
7. **음원 내보내기** 버튼 클릭 — 기본 파일명은 `{음원명}_{파형}_{Hz}_{offset}dB` (바이노럴: `{음원명}_stereo_{L파형}_{L_Hz}Hz_{R파형}_{R_Hz}Hz_{offset}dB`) 형식으로 자동 입력

## 프로젝트 구조

```
Wave_Blender/
├── main.py                     # 엔트리 포인트
├── requirements.txt
├── wave_blender/
│   ├── audio_loader.py         # 음원 로드 + 볼륨 정규화
│   ├── wave_synth.py           # 파형 생성 (numpy/scipy)
│   ├── mixer.py                # 믹싱 + 클리핑 방지
│   ├── exporter.py             # WAV/MP3/MP4 export
│   └── ui/
│       └── app.py              # tkinter GUI
└── scripts/
    └── build.bat               # PyInstaller 빌드 스크립트
```

## 의존성

| 패키지 | 용도 |
|--------|------|
| pydub | 음원 로드, 볼륨 조절, export |
| numpy | 파형 샘플 생성 |
| scipy | square/sawtooth/triangle 파형 |
| imageio-ffmpeg | ffmpeg 바이너리 내장 (MP3/MP4 입출력) |
| audioop-lts | Python 3.13+ 호환성 |
