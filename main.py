#!/usr/bin/env python3.9
from __future__ import annotations

__author__ = "7mochi"
__email__ = "flyingcatdm@gmail.com"
__discord__ = "天矢七海#1926"

import os

# set working directory to the project/ directory.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

description = """Simple bot que genera globos de texto"""

import asyncio
import uuid
import discord
import requests
from asyncio.events import AbstractEventLoop
from aiostream import stream
from PIL import Image
from functools import partial
from pathlib import Path
from signal import Signals, SIGINT, SIGTERM
from sys import stderr
from discord.ext import commands
from signal import SIGINT, SIGTERM
from typing import Optional

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

DATA_PATH = Path.cwd() / ".data"
DISCORD_IMAGES_PATH = DATA_PATH / "discord_images"
GLOBOS_TEMPLATES_PATH = DATA_PATH / "globos_templates"
GLOBO_FILE_PATH = GLOBOS_TEMPLATES_PATH / "globo.png"


class SignalHaltError(SystemExit):
    def __init__(self, signal_enum: Signals):
        self.signal_enum = signal_enum
        print(repr(self), file=stderr)
        super().__init__(self.exit_code)

    @property
    def exit_code(self) -> int:
        return self.signal_enum.value

    def __repr__(self) -> str:
        return f"\nExitted due to {self.signal_enum.name}"


def immediate_exit(signal_enum: Signals, loop: AbstractEventLoop) -> None:
    loop.stop()
    raise SignalHaltError(signal_enum=signal_enum)


class Context(commands.Context):
    async def send(self, content=None, **kwargs) -> Optional[discord.Message]:
        assert self.message is not None
        assert self.bot is not None

        return await super().send(content, **kwargs)


class Commands(commands.Cog):
    def __init__(self, bot: Globeado) -> None:
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx: Context) -> None:
        assert ctx.message is not None
        await ctx.send("QUE RICO EL ANASO DEL HECTORINE")

    @commands.command(name="sexo")
    async def sexo(self, ctx: Context) -> None:
        assert ctx.message is not None

        if not (ref_msg := ctx.message.reference):
            old_msgs = await stream.list(ctx.channel.history(limit=100))
            for old_msg in old_msgs:
                if len(old_msg.attachments) > 0:
                    msg = old_msg
                    break
        else:
            if ref_msg.cached_message is None:
                assert ref_msg.message_id is not None
                msg = await ctx.fetch_message(ref_msg.message_id)
            else:
                msg = ref_msg.cached_message

        globo = await self.process(msg)  # type: ignore

        assert globo is not None
        with open(globo, "rb") as file:
            to_send = discord.File(file)
            await ctx.send(file=to_send)
            os.remove(globo)

    async def process(self, msg: discord.Message) -> Optional[Path]:
        if len(msg.embeds) > 0:
            return await self.globear(msg.embeds[0].url)
        elif len(msg.attachments) > 0:
            return await self.globear(msg.attachments[0].url)

    async def globear(self, url: Optional[str]) -> Path:
        img_path = DISCORD_IMAGES_PATH / f"{str(uuid.uuid4())}.png"
        downloadFile(url, img_path)
        return self.merge_images_vertically(img_path)

    def merge_images_vertically(self, path: Path) -> Path:
        globo_img = Image.open(GLOBO_FILE_PATH)
        img = Image.open(path)

        if globo_img.width == img.width:
            _globo_img = globo_img
            _img = img
        elif (globo_img.width > img.width) or (globo_img.width < img.width):
            _globo_img = globo_img.resize(
                (img.width, int(globo_img.height * img.width / globo_img.width)),
                resample=Image.Resampling.BICUBIC,
            )
            _img = img
        else:
            _globo_img = globo_img
            _img = img.resize(
                (globo_img.width, int(img.height * globo_img.width / img.width)),
                resample=Image.Resampling.BICUBIC,
            )

        dst = Image.new("RGB", (_globo_img.width, _globo_img.height + _img.height))
        dst.paste(_globo_img, (0, 0))
        dst.paste(_img, (0, _globo_img.height))

        globeado_path = DATA_PATH / f"{str(uuid.uuid4())}.gif"
        dst.save(globeado_path)

        os.remove(path)

        return globeado_path


class Globeado(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def setup(self):
        await self.add_cog(Commands(self))

    async def run(self, token: str, *args, **kwargs) -> None:
        try:
            await self.start(token, *args, **kwargs)
        except:
            await self.close()

    async def process_commands(self, msg: discord.Message) -> None:
        if msg.author.bot:
            return

        ctx = await self.get_context(msg, cls=Context)
        await self.invoke(ctx)

    async def on_ready(self):
        assert self.user is not None
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, msg: discord.Message) -> None:
        await self.process_commands(msg)


def downloadFile(url: Optional[str], path: Path) -> bool:
    assert url is not None
    resp = requests.get(url)
    if resp.status_code != 200:
        return False

    path.write_bytes(resp.content)

    return True


async def ensure_directory_structure() -> int:
    """Ensure the .data directory"""
    DATA_PATH.mkdir(exist_ok=True)

    if not DISCORD_IMAGES_PATH.exists():
        DISCORD_IMAGES_PATH.mkdir(parents=True)

    if not GLOBOS_TEMPLATES_PATH.exists():
        GLOBOS_TEMPLATES_PATH.mkdir(parents=True)
        downloadFile(
            "https://cdn.discordapp.com/attachments/868266476061224971/1060980757100757173/globosexo.png",
            GLOBO_FILE_PATH,
        )

    return 0


async def main() -> int:
    loop = asyncio.get_running_loop()

    for signal_enum in [SIGINT, SIGTERM]:
        exit_func = partial(immediate_exit, signal_enum=signal_enum, loop=loop)
        loop.add_signal_handler(signal_enum, exit_func)

    await ensure_directory_structure()

    bot = Globeado(command_prefix="!", description=description, intents=intents)
    await bot.setup()
    await bot.run("REDACTED_TOKEN")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)
