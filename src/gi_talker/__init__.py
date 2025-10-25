# 패키지 버전을 pyproject.toml에서 가져오기 위한 헬퍼
from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    # 패키지가 설치되지 않은 개발 환경에서도 안전하게 동작하도록 처리
    try:
        return version("gi-talker")
    except PackageNotFoundError:
        return "0.0.0"

