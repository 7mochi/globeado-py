from __future__ import annotations

import io
import tempfile
from ast import alias
from encodings import aliases
from pathlib import Path
from typing import Any

import discord
from aiostream import stream
from discord import Message
from discord.ext import commands

from app.bot.globeado_bot import GlobeadoBot
from app.common import logger
from app.common import utils
from app.common.utils import GLOBO_FILE_PATH


class Commands(commands.Cog):
    """A cog that contains commands for the bot."""

    def __init__(self, bot: GlobeadoBot) -> None:
        self.bot = bot

    @commands.command(
        name="globodesexo",
        aliases=["globosexo", "globear", "globo", "gs"],
    )
    async def globodesexo(self, ctx: commands.Context[GlobeadoBot]) -> None:
        assert ctx.message is not None

        msg = None
        if not (ref_msg := ctx.message.reference):
            async for old_msg in ctx.channel.history(limit=100):
                if len(old_msg.attachments) > 0 or len(old_msg.embeds) > 0:
                    msg = old_msg
                    break
        else:
            if ref_msg.cached_message is None:
                assert ref_msg.message_id is not None
                msg = await ctx.fetch_message(ref_msg.message_id)
            else:
                msg = ref_msg.cached_message

        assert msg is not None
        image = await self.process(msg)

        assert image is not None
        await ctx.send(file=discord.File(fp=io.BytesIO(image), filename="globo.gif"))

    async def process(self, msg: Message) -> bytes | None:
        if len(msg.embeds) > 0:
            embed = msg.embeds[0]

            if embed.thumbnail.proxy_url is not None:
                return await self.globear(embed.thumbnail.proxy_url)
            elif embed.image.proxy_url is not None:
                return await self.globear(embed.image.proxy_url)
        elif len(msg.attachments) > 0:
            return await self.globear(msg.attachments[0].proxy_url)

        return None

    async def globear(self, url: str) -> bytes:
        return utils.merge_globo_with_image_vertically(
            image_bytes=utils.download_file(url),
        )
