from __future__ import annotations

import asyncio
import atexit

import discord

from app.bot.globeado_bot import GlobeadoBot
from app.common import logger
from app.common import settings

logger.configure_logging(
    app_env=settings.APP_ENV,
    log_level=settings.APP_LOG_LEVEL,
)
logger.overwrite_exception_hook()
atexit.register(logger.restore_exception_hook)

intents = discord.Intents.default()
intents.message_content = True


async def main() -> None:
    bot = GlobeadoBot(command_prefix="!", intents=intents)
    await bot.setup()
    try:
        await bot.start(settings.DISCORD_TOKEN)
    except asyncio.CancelledError:
        logger.info("Shutting down the bot...")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
