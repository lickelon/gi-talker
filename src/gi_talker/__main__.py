import asyncio

from .bot import KokoroTTSBot, register_commands
from .config import load_settings
from .logging_setup import configure_logging
from .tts import KokoroEngine


async def run_bot() -> None:
    # 로깅을 가장 먼저 초기화해 이후 단계에서 발생할 로그를 잡는다
    configure_logging()
    # .env 기반 설정 로딩
    settings = load_settings()
    # Kokoro 엔진은 환경 변수에서 지정한 모델/음성을 사용해 초기화
    engine = KokoroEngine(
        model_path=settings.kokoro_model_path,
        voices_path=settings.kokoro_voices_path,
        default_voice=settings.kokoro_default_voice,
        default_locale=settings.kokoro_default_locale,
        default_speed=settings.kokoro_default_speed,
    )
    bot = KokoroTTSBot(settings=settings, tts_engine=engine)
    register_commands(bot)
    await bot.start(settings.token)


def main() -> None:
    # asyncio 실행 환경에서 봇을 구동
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
