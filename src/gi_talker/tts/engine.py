from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np


try:
    # MeloTTS는 설치 시 `melo` 패키지를 제공한다.
    from melo.api import TTS as MeloTTS
except ImportError as exc:  # pragma: no cover - 런타임 환경에 따라 발생 가능
    raise RuntimeError("MeloTTS 패키지가 설치되어 있지 않습니다.") from exc


@dataclass
class SynthesisRequest:
    # 음성으로 변환할 텍스트
    text: str
    # 화자 이름
    speaker: Optional[str] = None
    # 화자 ID
    speaker_id: Optional[int] = None
    # 합성 속도
    speed: Optional[float] = None
    # 합성 품질 관련 파라미터
    sdp_ratio: Optional[float] = None
    noise_scale: Optional[float] = None
    noise_scale_w: Optional[float] = None


@dataclass
class SynthesisResult:
    # 생성된 PCM 데이터를 바이트 형태로 보관
    pcm: bytes
    # 샘플레이트는 재생 파이프라인에서 변환 여부를 결정
    sample_rate: int


class MeloTtsEngine:
    def __init__(
        self,
        *,
        language: str,
        default_speaker: Optional[str] = None,
        default_speaker_id: Optional[int] = None,
        device: Optional[str] = None,
        use_hf: bool = True,
        default_speed: float = 1.0,
        default_sdp_ratio: float = 0.2,
        default_noise_scale: float = 0.6,
        default_noise_scale_w: float = 0.8,
    ) -> None:
        self._language = language
        self._default_speaker = default_speaker
        self._default_speaker_id = default_speaker_id
        self._device = device or "auto"
        self._use_hf = use_hf
        self._default_speed = default_speed
        self._default_sdp_ratio = default_sdp_ratio
        self._default_noise_scale = default_noise_scale
        self._default_noise_scale_w = default_noise_scale_w

        self._model: Optional[MeloTTS] = None
        self._speaker_map: Dict[str, int] = {}
        self._load_lock = threading.Lock()

    def load(self) -> None:
        if self._model is not None:
            return

        with self._load_lock:
            if self._model is not None:
                return

            self._model = MeloTTS(
                language=self._language,
                device=self._device,
                use_hf=self._use_hf,
            )
            spk2id = getattr(self._model.hps.data, "spk2id", {}) or {}
            self._speaker_map = dict(spk2id)
            if not self._speaker_map:
                raise RuntimeError(
                    f"{self._language} 언어에 대한 화자 정보를 불러오지 못했습니다."
                )

            # 기본 화자 ID가 지정되어 있지 않다면 이름 또는 첫 번째 화자를 사용
            if self._default_speaker_id is None:
                if self._default_speaker and self._default_speaker in self._speaker_map:
                    self._default_speaker_id = self._speaker_map[self._default_speaker]
                else:
                    self._default_speaker_id = next(iter(self._speaker_map.values()))

    def available_speakers(self) -> Dict[str, int]:
        self.load()
        assert self._model is not None
        return dict(self._speaker_map)

    def _select_speaker_id(self, request: SynthesisRequest) -> int:
        if request.speaker_id is not None:
            return request.speaker_id

        if request.speaker:
            # 화자 이름이 존재하면 매핑에서 찾아 ID 사용
            if request.speaker in self._speaker_map:
                return self._speaker_map[request.speaker]
            # 숫자 문자열이면 ID로 간주
            if request.speaker.isdigit():
                return int(request.speaker)
            raise ValueError(
                f"'{request.speaker}' 화자를 찾을 수 없습니다. 사용 가능: {', '.join(self._speaker_map)}"
            )

        if self._default_speaker_id is not None:
            return self._default_speaker_id

        raise ValueError("사용 가능한 기본 화자가 설정되지 않았습니다.")

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        self.load()
        assert self._model is not None

        speaker_id = self._select_speaker_id(request)
        speed = request.speed if request.speed is not None else self._default_speed
        if speed <= 0:
            raise ValueError("합성 속도는 0보다 커야 합니다.")

        sdp_ratio = (
            request.sdp_ratio if request.sdp_ratio is not None else self._default_sdp_ratio
        )
        noise_scale = (
            request.noise_scale
            if request.noise_scale is not None
            else self._default_noise_scale
        )
        noise_scale_w = (
            request.noise_scale_w
            if request.noise_scale_w is not None
            else self._default_noise_scale_w
        )

        audio = self._model.tts_to_file(
            text=request.text,
            speaker_id=speaker_id,
            output_path=None,
            sdp_ratio=sdp_ratio,
            noise_scale=noise_scale,
            noise_scale_w=noise_scale_w,
            speed=speed,
            quiet=True,
        )

        pcm = np.clip(audio, -1.0, 1.0)
        pcm = (pcm * np.iinfo(np.int16).max).astype(np.int16)

        sample_rate = int(getattr(self._model.hps.data, "sampling_rate", 44100))

        return SynthesisResult(
            pcm=pcm.tobytes(),
            sample_rate=sample_rate,
        )
