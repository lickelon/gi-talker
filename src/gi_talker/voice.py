# 디스코드 음성 채널 관리 유틸리티
from __future__ import annotations

import asyncio
from typing import Optional

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

    async def play_pcm(self, pcm_path: str) -> None:
        # FFmpeg 기반 오디오 소스로 PCM 파일 재생 (추후 스트림 교체 예정)
        async with self._play_lock:
            source = discord.FFmpegPCMAudio(pcm_path)
            self._voice_client.play(source)
            # discord.py는 blocking 재생이므로 완료까지 poll
            while self._voice_client.is_playing():
                await asyncio.sleep(0.1)

    async def disconnect(self) -> None:
        # 호출자가 명시적으로 연결 종료 가능하도록 메서드 제공
        await self._voice_client.disconnect()


async def ensure_voice(
    bot: discord.Client,
    target_channel: discord.VoiceChannel,
) -> VoiceSession:
    # 이미 연결된 경우 기존 세션 재사용
    if target_channel.guild.voice_client:
        return VoiceSession(target_channel.guild.voice_client)

    # 새 연결을 생성하고 세션 래핑
    voice_client = await target_channel.connect()
    return VoiceSession(voice_client)

