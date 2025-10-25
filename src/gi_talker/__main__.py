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
    # Kokoro 엔진은 현재 자리 표시자이므로 모델 경로는 추후 전달
    engine = KokoroEngine(model_path=settings_path_placeholder())
    bot = KokoroTTSBot(settings=settings, tts_engine=engine)
    register_commands(bot)
    await bot.start(settings.token)


def settings_path_placeholder():
    # 모델 경로가 확정되기 전까지 임시 Path 객체를 반환
    from pathlib import Path

    return Path("models/kokoro-82m.onnx")


def main() -> None:
    # asyncio 실행 환경에서 봇을 구동
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
