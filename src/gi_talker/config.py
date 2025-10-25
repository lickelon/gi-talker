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
    # MeloTTS 기본 언어 코드 (예: KR, EN, JP)
    melotts_language: str = "KR"
    # 화자 이름(환경에 따라 존재하는 이름이어야 함)
    melotts_speaker: Optional[str] = None
    # 화자 ID를 직접 지정할 수도 있음
    melotts_speaker_id: Optional[int] = None
    # 디바이스(auto/cpu/cuda/mps)
    melotts_device: Optional[str] = None
    # Hugging Face에서 모델을 내려받을지 여부
    melotts_use_hf: bool = True
    # 합성 속도
    melotts_speed: float = 1.0
    # 합성 시 사용되는 파라미터들
    melotts_sdp_ratio: float = 0.2
    melotts_noise_scale: float = 0.6
    melotts_noise_scale_w: float = 0.8


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

    melotts_language = os.getenv("MELOTTS_LANGUAGE", "KR")
    melotts_speaker = os.getenv("MELOTTS_SPEAKER")
    speaker_id_raw = os.getenv("MELOTTS_SPEAKER_ID")
    melotts_speaker_id = int(speaker_id_raw) if speaker_id_raw else None
    melotts_device = os.getenv("MELOTTS_DEVICE")
    use_hf_raw = os.getenv("MELOTTS_USE_HF", "true").lower()
    melotts_use_hf = use_hf_raw not in {"false", "0", "no"}
    speed_raw = os.getenv("MELOTTS_SPEED")
    melotts_speed = float(speed_raw) if speed_raw else 1.0
    sdp_ratio_raw = os.getenv("MELOTTS_SDP_RATIO")
    melotts_sdp_ratio = float(sdp_ratio_raw) if sdp_ratio_raw else 0.2
    noise_scale_raw = os.getenv("MELOTTS_NOISE_SCALE")
    melotts_noise_scale = float(noise_scale_raw) if noise_scale_raw else 0.6
    noise_scale_w_raw = os.getenv("MELOTTS_NOISE_SCALE_W")
    melotts_noise_scale_w = float(noise_scale_w_raw) if noise_scale_w_raw else 0.8

    return BotSettings(
        token=token,
        default_voice_channel_id=channel_id,
        command_prefix=prefix,
        melotts_language=melotts_language,
        melotts_speaker=melotts_speaker,
        melotts_speaker_id=melotts_speaker_id,
        melotts_device=melotts_device,
        melotts_use_hf=melotts_use_hf,
        melotts_speed=melotts_speed,
        melotts_sdp_ratio=melotts_sdp_ratio,
        melotts_noise_scale=melotts_noise_scale,
        melotts_noise_scale_w=melotts_noise_scale_w,
    )
