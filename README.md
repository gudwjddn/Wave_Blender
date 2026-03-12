# Wave Blender

보유 음원 파일에 합성 파형(사인파, 사각파, 톱니파, 삼각파)을 오버레이하여 export하는 Windows 데스크톱 앱.

## 주요 기능

- **음원 자동 정규화**: 파일마다 다른 볼륨을 -20 dBFS로 자동 통일
- **파형 오버레이**: Sine / Square / Sawtooth / Triangle 파형 선택
- **주파수 설정**: 1 ~ 20,000 Hz 자유 입력
- **볼륨 오프셋**: 파형 볼륨을 원본 대비 dB 단위로 조절 (기본값 -6 dB)
- **클리핑 방지**: 믹싱 후 peak -1 dBFS 초과 시 자동 gain 감소
- **WAV / MP3 export** (ffmpeg 별도 설치 불필요)

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

빌드 결과물: `dist/WaveBlender.exe`

> PyInstaller 설치 필요: `pip install pyinstaller`

## 사용법

1. **찾아보기** 버튼으로 음원 파일 선택 (.wav, .mp3, .ogg, .flac 등)
2. 파형 종류, 주파수(Hz), 볼륨 오프셋(dB) 설정
3. 출력 포맷 선택 (WAV / MP3)
4. **음원 내보내기** 버튼 클릭 후 저장 위치 지정

## 프로젝트 구조

```
Wave_Blender/
├── main.py                     # 엔트리 포인트
├── requirements.txt
├── wave_blender/
│   ├── audio_loader.py         # 음원 로드 + 볼륨 정규화
│   ├── wave_synth.py           # 파형 생성 (numpy/scipy)
│   ├── mixer.py                # 믹싱 + 클리핑 방지
│   ├── exporter.py             # WAV/MP3 export
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
| imageio-ffmpeg | ffmpeg 바이너리 내장 (MP3 입출력) |
| audioop-lts | Python 3.13+ 호환성 |
