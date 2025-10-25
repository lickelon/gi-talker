# 디스코드 봇의 기본 동작을 담당하는 모듈
from __future__ import annotations

import logging
from typing import Optional

import discord
from discord import app_commands

from .config import BotSettings
from .tts import MeloTtsEngine, SynthesisRequest
from .voice import VoiceSession, ensure_voice


class MeloTTSBot(discord.Client):
    def __init__(self, settings: BotSettings, tts_engine: MeloTtsEngine) -> None:
        self._settings = settings
        self._tts_engine = tts_engine
        self._logger = logging.getLogger("gi_talker.bot")
        self._voice_session: Optional[VoiceSession] = None
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()
        self._logger.debug("Slash commands synchronized")

    async def on_ready(self) -> None:
        self._logger.info("로그인 완료: %s", self.user)

    async def _resolve_target_channel(
        self, interaction: discord.Interaction
    ) -> discord.VoiceChannel:
        user_voice = getattr(interaction.user, "voice", None)
        if user_voice and user_voice.channel:
            return user_voice.channel

        if self._settings.default_voice_channel_id:
            channel = self.get_channel(self._settings.default_voice_channel_id)
            if isinstance(channel, discord.VoiceChannel):
                return channel

        raise RuntimeError("음성 채널에 접속 중이 아니며 기본 채널도 설정되지 않았습니다.")

    async def _ensure_session(self, interaction: discord.Interaction) -> VoiceSession:
        if (
            self._voice_session
            and interaction.guild
            and self._voice_session.channel.guild.id == interaction.guild.id
        ):
            return self._voice_session

        target_channel = await self._resolve_target_channel(interaction)
        self._voice_session = await ensure_voice(target_channel)
        return self._voice_session

    async def close(self) -> None:
        if self._voice_session:
            await self._voice_session.disconnect()
        await super().close()


def register_commands(bot: MeloTTSBot) -> None:
    @bot.tree.command(name="ping", description="봇 상태 확인")
    async def ping(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("pong", ephemeral=True)

    @bot.tree.command(name="join", description="현재 음성 채널에 봇을 초대합니다.")
    async def join(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            session = await bot._ensure_session(interaction)
        except RuntimeError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return

        await interaction.followup.send(
            f"{session.channel.name} 채널에 연결했어요.", ephemeral=True
        )

    @bot.tree.command(name="leave", description="봇을 음성 채널에서 내보냅니다.")
    async def leave(interaction: discord.Interaction) -> None:
        if bot._voice_session:
            await bot._voice_session.disconnect()
            bot._voice_session = None
            await interaction.response.send_message(
                "음성 채널에서 나왔어요.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "연결된 음성 채널이 없어요.", ephemeral=True
            )

    @bot.tree.command(name="say", description="텍스트를 음성으로 재생합니다.")
    @app_commands.describe(text="재생할 메시지")
    async def say(interaction: discord.Interaction, text: str) -> None:
        await interaction.response.send_message("TTS를 재생할게요.", ephemeral=True)
        try:
            session = await bot._ensure_session(interaction)
        except RuntimeError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return

        request = SynthesisRequest(
            text=text,
            speaker=bot._settings.melotts_speaker,
            speaker_id=bot._settings.melotts_speaker_id,
            speed=bot._settings.melotts_speed,
            sdp_ratio=bot._settings.melotts_sdp_ratio,
            noise_scale=bot._settings.melotts_noise_scale,
            noise_scale_w=bot._settings.melotts_noise_scale_w,
        )
        try:
            result = bot._tts_engine.synthesize(request)
        except ValueError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return
        except RuntimeError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return
        except Exception as exc:
            bot._logger.exception("합성 실패", exc_info=exc)
            await interaction.followup.send(
                "합성 중 오류가 발생했어요.", ephemeral=True
            )
            return

        try:
            await session.play_pcm(result.pcm, result.sample_rate)
        except Exception as exc:
            bot._logger.exception("재생 실패", exc_info=exc)
            await interaction.followup.send(
                "재생 중 문제가 발생했어요.", ephemeral=True
            )
