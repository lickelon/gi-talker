# MeloTTS 디스코드 TTS 봇

MeloTTS 멀티언어 음성 합성 모델과 `discord.py`를 이용해 텍스트를 디스코드 음성 채널에서 재생하는 봇 프로젝트입니다. 기본값은 한국어(`KR`) 화자를 사용하지만 언어/화자를 손쉽게 교체할 수 있습니다.

## 준비물

- Python 3.12 (uv가 자동으로 관리)
- [uv](https://docs.astral.sh/uv/) 패키지 매니저
- FFmpeg 실행 파일 (PATH에 포함)
- 디스코드 봇 토큰 및 음성 채널 권한
- (선택) GPU가 있으면 추론이 더 빠르지만 CPU만으로도 동작 가능

## 설치

```bash
git clone https://github.com/lickelon/gi-talker.git
cd gi-talker
uv sync --extra melotts
```

## 환경 설정

```bash
cp .env.example .env
```

`.env` 파일에 아래 항목을 채웁니다.

- `DISCORD_BOT_TOKEN`: 디스코드 봇 토큰
- `DEFAULT_VOICE_CHANNEL_ID`: 기본 음성 채널 ID (옵션)
- `MELOTTS_LANGUAGE`: 사용할 언어 코드 (예: `KR`, `EN`, `JP`, `ZH`, ...)
- `MELOTTS_SPEAKER` 또는 `MELOTTS_SPEAKER_ID`: 기본 화자 이름/ID
- `MELOTTS_SPEED`, `MELOTTS_SDP_RATIO`, `MELOTTS_NOISE_SCALE(_W)`: 합성 파라미터 (옵션)
- 나머지 항목은 `.env.example` 참고

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
- 첫 실행 시 MeloTTS가 Hugging Face에서 모델을 자동으로 내려받으므로 네트워크가 필요합니다.
- PyNaCl이 설치되지 않았다면 `uv add pynacl` 후 다시 실행하세요.
