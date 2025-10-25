# 디스코드 봇의 기본 동작을 담당하는 모듈
from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from .config import BotSettings
from .tts import MeloTtsEngine, SynthesisRequest
from .voice import VoiceSession, ensure_voice


class MeloTTSBot(commands.Bot):
    def __init__(self, settings: BotSettings, tts_engine: MeloTtsEngine) -> None:
        # 봇 동작에 필요한 설정과 의존성을 저장
        self._settings = settings
        self._tts_engine = tts_engine
        self._logger = logging.getLogger("gi_talker.bot")
        self._voice_session: Optional[VoiceSession] = None

        intents = discord.Intents.default()
        # 텍스트 명령어 처리를 위해 message_content 권한 활성화
        intents.message_content = True

        super().__init__(command_prefix=settings.command_prefix, intents=intents)

    async def setup_hook(self) -> None:
        # 추후 슬래시 커맨드 동기화 등을 수행할 진입점
        self._logger.debug("Bot setup hook initialized")

    async def on_ready(self) -> None:
        # 봇이 정상적으로 로그인했음을 콘솔에 출력
        self._logger.info("로그인 완료: %s", self.user)

    async def _resolve_target_channel(
        self, ctx: commands.Context
    ) -> discord.VoiceChannel:
        # 명령을 실행한 사용자의 음성 채널을 우선 사용
        if ctx.author.voice and ctx.author.voice.channel:
            return ctx.author.voice.channel

        # 기본 채널 ID가 설정되어 있다면 그 채널을 사용
        if self._settings.default_voice_channel_id:
            channel = self.get_channel(self._settings.default_voice_channel_id)
            if isinstance(channel, discord.VoiceChannel):
                return channel

        raise commands.CommandError("음성 채널에 접속 중이 아니며 기본 채널도 설정되지 않았습니다.")

    async def cog_check(self, ctx: commands.Context) -> bool:
        # 모든 명령에서 공통적으로 필요한 검증 로직을 배치 가능
        return True

    async def _ensure_session(
        self, ctx: commands.Context
    ) -> VoiceSession:
        # 기존 세션이 있고 동일 길드라면 재사용
        if (
            self._voice_session
            and self._voice_session.channel.guild.id == ctx.guild.id
        ):
            return self._voice_session

        target_channel = await self._resolve_target_channel(ctx)
        self._voice_session = await ensure_voice(target_channel)
        return self._voice_session

    async def close(self) -> None:
        # 봇 종료 시 음성 연결을 정리
        if self._voice_session:
            await self._voice_session.disconnect()
        await super().close()


def register_commands(bot: MeloTTSBot) -> None:
    # ping 명령은 헬스체크 용도로 사용
    @bot.command()
    async def ping(ctx: commands.Context) -> None:
        await ctx.reply("pong")

    # join 명령으로 음성 채널 접속
    @bot.command()
    async def join(ctx: commands.Context) -> None:
        session = await bot._ensure_session(ctx)
        await ctx.reply(f"{session.channel.name} 채널에 연결했어요.")

    # leave 명령으로 음성 채널 퇴장
    @bot.command()
    async def leave(ctx: commands.Context) -> None:
        if bot._voice_session:
            await bot._voice_session.disconnect()
            bot._voice_session = None
            await ctx.reply("음성 채널에서 나왔어요.")
        else:
            await ctx.reply("연결된 음성 채널이 없어요.")

    # say 명령은 TTS를 호출하는 핵심 기능의 골격
    @bot.command()
    async def say(ctx: commands.Context, *, text: str) -> None:
        session = await bot._ensure_session(ctx)
        await ctx.reply(f"{session.channel.name} 채널로 음성을 전송할 준비를 해볼게요.")

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
            await ctx.reply(str(exc))
            return
        except RuntimeError as exc:
            await ctx.reply(str(exc))
            return
        except Exception as exc:
            bot._logger.exception("합성 실패", exc_info=exc)
            await ctx.reply("합성 중 오류가 발생했어요.")
            return

        await ctx.reply(
            f"샘플레이트 {result.sample_rate}Hz 합성 데이터를 확보했어요. 재생을 시작할게요."
        )

        try:
            await session.play_pcm(result.pcm, result.sample_rate)
        except Exception as exc:
            bot._logger.exception("재생 실패", exc_info=exc)
            await ctx.reply("재생 중 문제가 발생했어요.")
            return

        await ctx.reply("재생을 마쳤어요.")
