from __future__ import annotations

from typing import Any

from discord import Message
from discord.ext.commands import Bot
from discord.ext.commands import Context as BaseContext


class Context(BaseContext[Bot]):
    async def send(self, content: str | None = None, **kwargs: Any) -> Message:
        assert self.message is not None
        assert self.bot is not None

        return await super().send(content, **kwargs)
