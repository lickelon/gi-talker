# Kokoro-82M 디스코드 TTS 봇

Kokoro-82M 음성 합성 모델과 `discord.py`를 이용해 텍스트를 디스코드 음성 채널에서 재생하는 봇 프로젝트입니다.

## 준비물

- Python 3.12 (uv가 자동으로 관리)
- [uv](https://docs.astral.sh/uv/) 패키지 매니저
- FFmpeg 실행 파일 (PATH에 포함)
- 디스코드 봇 토큰 및 음성 채널 권한
- Kokoro 모델 파일과 음성 임베딩

모델 자원은 아래와 같이 내려받아 `models/` 디렉터리에 배치합니다.

```bash
mkdir -p models
curl -L -o models/kokoro-82m.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-82m.onnx
curl -L -o models/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

## 설치

```bash
git clone https://github.com/lickelon/gi-talker.git
cd gi-talker
uv sync
```

## 환경 설정

```bash
cp .env.example .env
```

`.env` 파일에 아래 항목을 채웁니다.

- `DISCORD_BOT_TOKEN`: 디스코드 봇 토큰
- `DEFAULT_VOICE_CHANNEL_ID`: 기본 음성 채널 ID (옵션)
- `KOKORO_MODEL_PATH`, `KOKORO_VOICES_PATH`: 모델/음성 파일 경로 (기본값: `models/` 하위)
- `KOKORO_DEFAULT_VOICE`, `KOKORO_DEFAULT_LOCALE`, `KOKORO_DEFAULT_SPEED`: 기본 합성 설정 (옵션)

## 실행

```bash
uv run python -m gi_talker
```

디스코드에서 명령 프리픽스(`!`)를 사용해 다음 명령을 호출할 수 있습니다.

- `!join`: 현재 음성 채널 또는 기본 채널에 접속
- `!leave`: 음성 채널에서 퇴장
- `!say <텍스트>`: 텍스트를 합성해 재생
- `!ping`: 상태 확인

## 주의 사항

- FFmpeg가 설치되어 있고 PATH에 등록되어 있어야 합니다.
- 모델 및 음성 파일은 메모리를 많이 사용하므로 서버 자원 여유를 확인하세요.
