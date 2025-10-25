import asyncio

from .bot import MeloTTSBot, register_commands
from .config import load_settings
from .logging_setup import configure_logging
from .tts import MeloTtsEngine


async def run_bot() -> None:
    # 로깅을 가장 먼저 초기화해 이후 단계에서 발생할 로그를 잡는다
    configure_logging()
    # .env 기반 설정 로딩
    settings = load_settings()
    # MeloTTS 엔진을 설정 값으로 초기화
    engine = MeloTtsEngine(
        language=settings.melotts_language,
        default_speaker=settings.melotts_speaker,
        default_speaker_id=settings.melotts_speaker_id,
        device=settings.melotts_device,
        use_hf=settings.melotts_use_hf,
        default_speed=settings.melotts_speed,
        default_sdp_ratio=settings.melotts_sdp_ratio,
        default_noise_scale=settings.melotts_noise_scale,
        default_noise_scale_w=settings.melotts_noise_scale_w,
    )
    bot = MeloTTSBot(settings=settings, tts_engine=engine)
    register_commands(bot)
    await bot.start(settings.token)


def main() -> None:
    # asyncio 실행 환경에서 봇을 구동
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
