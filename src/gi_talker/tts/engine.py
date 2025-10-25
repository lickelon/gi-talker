# Kokoro-82M 추론을 감싸는 엔진 스켈레톤
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SynthesisRequest:
    # 음성으로 변환할 텍스트
    text: str
    # 화자 ID 혹은 프리셋을 문자열로 지정
    speaker: str = "default"
    # 추론 시 사용할 언어 코드
    locale: str = "ko-KR"


@dataclass
class SynthesisResult:
    # 생성된 PCM 데이터를 바이트 형태로 보관
    pcm: bytes
    # 샘플레이트는 재생 파이프라인에서 변환 여부를 결정
    sample_rate: int


class KokoroEngine:
    def __init__(self, model_path: Path, device: Optional[str] = None) -> None:
        # 모델 경로와 디바이스 선택을 저장해두고 지연 로딩 전략을 적용
        self._model_path = model_path
        self._device = device or "cpu"
        self._model = None

    def load(self) -> None:
        # 실제 모델 로딩 로직은 추후 구현, 현재는 자리 표시자
        if self._model is None:
            # TODO: Kokoro 82M 로더 통합
            self._model = object()

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        # 예외 메시지로 미구현 상태를 명확히 전달
        raise NotImplementedError("KokoroEngine.synthesize()는 추후 구현 예정입니다.")

