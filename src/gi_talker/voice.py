from __future__ import annotations

import asyncio
import os
import tempfile

import numpy as np
import discord


class VoiceSession:
    def __init__(self, voice_client: discord.VoiceClient) -> None:
        # 재생 중인 작업을 추적해 중복 재생을 방지
        self._voice_client = voice_client
        self._play_lock = asyncio.Lock()

    @property
    def channel(self) -> discord.VoiceChannel:
        # 현재 연결된 채널을 노출
        return self._voice_client.channel

    async def play_pcm(self, pcm: bytes, sample_rate: int) -> None:
        # 합성 결과를 임시 WAV 파일로 저장 후 FFmpeg를 통해 재생
        async with self._play_lock:
            wav_path = self._write_temp_wav(pcm, sample_rate)
            try:
                source = discord.FFmpegPCMAudio(
                    wav_path,
                    before_options="-loglevel warning",
                    options="-f s16le -ac 2 -ar 48000",
                )
                self._voice_client.play(source)
                # discord.py는 blocking 재생이므로 완료까지 poll
                while self._voice_client.is_playing():
                    await asyncio.sleep(0.1)
            finally:
                if os.path.exists(wav_path):
                    os.remove(wav_path)

    async def disconnect(self) -> None:
        # 호출자가 명시적으로 연결 종료 가능하도록 메서드 제공
        await self._voice_client.disconnect()

    def _write_temp_wav(self, pcm: bytes, sample_rate: int) -> str:
        # numpy 배열로 변환해 soundfile을 통해 WAV 작성
        data = np.frombuffer(pcm, dtype=np.int16)
        with tempfile.NamedTemporaryFile("wb", suffix=".wav", delete=False) as tmp:
            from soundfile import write as sf_write

            sf_write(tmp.name, data, sample_rate, subtype="PCM_16")
            return tmp.name


async def ensure_voice(
    target_channel: discord.VoiceChannel,
) -> VoiceSession:
    # 이미 연결된 경우 기존 세션 재사용
    if target_channel.guild.voice_client:
        return VoiceSession(target_channel.guild.voice_client)

    # 새 연결을 생성하고 세션 래핑
    voice_client = await target_channel.connect()
    return VoiceSession(voice_client)
