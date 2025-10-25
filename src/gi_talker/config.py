# 환경 변수 기반 설정 로딩 모듈
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os

from dotenv import load_dotenv


# .env 파일을 자동으로 읽어 초기 설정을 준비
def _bootstrap_env() -> None:
    # 프로젝트 루트에 위치한 .env를 우선적으로 탐색
    dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    else:
        # .env가 없어도 시스템 환경 변수만으로 동작하도록 여지를 둠
        load_dotenv()


@dataclass
class BotSettings:
    # 디스코드 봇 토큰은 필수 항목
    token: str
    # 기본 음성 채널 ID를 미리 지정하면 연결 명령 단순화 가능
    default_voice_channel_id: Optional[int] = None
    # 이후 텍스트 전처리 등 옵션 추가를 고려해 확장 포인트 마련
    command_prefix: str = "!"
    # Kokoro 모델 파일 경로
    kokoro_model_path: Path = field(default_factory=lambda: Path("models/kokoro-82m.onnx"))
    # Kokoro 음성 임베딩 파일 경로
    kokoro_voices_path: Path = field(default_factory=lambda: Path("models/voices-v1.0.bin"))
    # 기본 음성 화자 지정
    kokoro_default_voice: Optional[str] = None
    # 기본 언어 코드
    kokoro_default_locale: str = "en-us"
    # 기본 발화 속도
    kokoro_default_speed: float = 1.0


def load_settings() -> BotSettings:
    # 먼저 .env 로드를 수행해 환경 변수를 확보
    _bootstrap_env()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        # 토큰이 없으면 즉시 실패시켜 설정 문제를 빠르게 인지
        raise RuntimeError("DISCORD_BOT_TOKEN is required")

    channel_id_raw = os.getenv("DEFAULT_VOICE_CHANNEL_ID")
    channel_id = int(channel_id_raw) if channel_id_raw else None

    prefix = os.getenv("COMMAND_PREFIX", "!")

    model_path = Path(
        os.getenv("KOKORO_MODEL_PATH", "models/kokoro-82m.onnx")
    ).expanduser()
    voices_path = Path(
        os.getenv("KOKORO_VOICES_PATH", "models/voices-v1.0.bin")
    ).expanduser()
    default_voice = os.getenv("KOKORO_DEFAULT_VOICE")
    default_locale = os.getenv("KOKORO_DEFAULT_LOCALE", "en-us")
    speed_raw = os.getenv("KOKORO_DEFAULT_SPEED")
    default_speed = float(speed_raw) if speed_raw else 1.0

    return BotSettings(
        token=token,
        default_voice_channel_id=channel_id,
        command_prefix=prefix,
        kokoro_model_path=model_path,
        kokoro_voices_path=voices_path,
        kokoro_default_voice=default_voice,
        kokoro_default_locale=default_locale,
        kokoro_default_speed=default_speed,
    )
