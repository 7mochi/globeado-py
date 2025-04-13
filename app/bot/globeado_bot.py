from __future__ import annotations

import asyncio
import logging
from typing import Any

from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot

from app.bot.context import Context
from app.common import logger

SHUTDOWN_TIMEOUT = 15


class GlobeadoBot(Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def setup(self) -> None:
        from app.bot.commands import Commands

        logging.info("Setting up the bot...")
        await self.add_cog(Commands(self))

    async def start(self, *args: Any, **kwargs: Any) -> None:
        logging.info("Starting bot...")
        try:
            await super().start(*args, **kwargs)
        except asyncio.CancelledError:
            await self.close()
            raise

    async def close(self) -> None:
        async def _shutdown() -> None:
            await commands.Bot.close(self)

        try:
            await asyncio.wait_for(_shutdown(), timeout=SHUTDOWN_TIMEOUT)
        except asyncio.CancelledError:
            logging.exception(
                "Shutdown timeout of %s exceeded, exiting immediately",
                SHUTDOWN_TIMEOUT,
                extra={"timeout": SHUTDOWN_TIMEOUT},
            )

    async def on_ready(self) -> None:
        assert self.user is not None
        logger.info(f"Logged in as {self.user} - ID: ({self.user.id})")

    async def process_commands(self, message: Message) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def on_message(self, message: Message) -> None:
        await self.process_commands(message)

    async def on_command_error(
        self,
        context: commands.Context[GlobeadoBot],  # type: ignore
        exception: commands.CommandError,
    ) -> None:
        if isinstance(exception, commands.CommandNotFound):
            return
        raise exception
