from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.environ["APP_ENV"]
APP_COMPONENT = os.environ["APP_COMPONENT"]
APP_LOG_LEVEL = os.environ["APP_LOG_LEVEL"]

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
