# 로깅 초기화 유틸리티
import logging
import sys


def configure_logging(verbose: bool = False) -> None:
    # verbose 옵션에 따라 로그 레벨을 조정
    level = logging.DEBUG if verbose else logging.INFO

    # 표준 출력으로 로그를 일관되게 보내도록 핸들러 구성
    handler = logging.StreamHandler(stream=sys.stdout)
    # 실행 중 문제를 빠르게 식별할 수 있도록 간결한 포맷 사용
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

