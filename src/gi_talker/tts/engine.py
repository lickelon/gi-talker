from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from kokoro_onnx import Kokoro
from kokoro_onnx.config import SAMPLE_RATE


@dataclass
class SynthesisRequest:
    # 음성으로 변환할 텍스트
    text: str
    # 화자 ID 혹은 프리셋을 문자열로 지정
    speaker: Optional[str] = None
    # 추론 시 사용할 언어 코드
    locale: Optional[str] = None
    # 발화 속도
    speed: Optional[float] = None
    # 무음 트리밍 여부
    trim: bool = True


@dataclass
class SynthesisResult:
    # 생성된 PCM 데이터를 바이트 형태로 보관
    pcm: bytes
    # 샘플레이트는 재생 파이프라인에서 변환 여부를 결정
    sample_rate: int


class KokoroEngine:
    def __init__(
        self,
        model_path: Path,
        voices_path: Path,
        *,
        default_voice: Optional[str] = None,
        default_locale: str = "en-us",
        default_speed: float = 1.0,
    ) -> None:
        # 모델 경로와 디바이스 선택을 저장해두고 지연 로딩 전략을 적용
        self._model_path = Path(model_path)
        self._voices_path = Path(voices_path)
        self._default_voice = default_voice
        self._default_locale = default_locale
        self._default_speed = default_speed
        self._model: Optional[Kokoro] = None
        self._load_lock = threading.Lock()

    def load(self) -> None:
        # 실제 모델 로딩 로직은 추후 구현, 현재는 자리 표시자
        if self._model is not None:
            return

        if not self._model_path.exists():
            raise FileNotFoundError(
                f"Kokoro 모델 파일을 찾을 수 없습니다: {self._model_path}"
            )
        if not self._voices_path.exists():
            raise FileNotFoundError(
                f"Kokoro 음성 파일을 찾을 수 없습니다: {self._voices_path}"
            )

        with self._load_lock:
            if self._model is None:
                self._model = Kokoro(
                    str(self._model_path),
                    str(self._voices_path),
                )

    def list_voices(self) -> list[str]:
        self.load()
        assert self._model is not None
        return self._model.get_voices()

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        self.load()
        assert self._model is not None

        voice = request.speaker or self._default_voice
        if not voice:
            raise ValueError("합성에 사용할 기본 음성을 설정하세요.")

        available = self._model.get_voices()
        if voice not in available:
            raise ValueError(
                f"'{voice}' 음성을 찾을 수 없습니다. 사용 가능: {', '.join(available)}"
            )

        locale = (request.locale or self._default_locale).lower()
        speed = request.speed if request.speed is not None else self._default_speed

        if not 0.5 <= speed <= 2.0:
            raise ValueError("발화 속도는 0.5 이상 2.0 이하만 허용됩니다.")

        audio, sample_rate = self._model.create(
            text=request.text,
            voice=voice,
            speed=speed,
            lang=locale,
            trim=request.trim,
        )

        # Kokoro는 float32 범위(-1.0~1.0)의 값을 반환하므로 16-bit PCM으로 변환
        pcm = np.clip(audio, -1.0, 1.0)
        pcm = (pcm * np.iinfo(np.int16).max).astype(np.int16)

        return SynthesisResult(
            pcm=pcm.tobytes(),
            sample_rate=sample_rate or SAMPLE_RATE,
        )
