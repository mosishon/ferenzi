import asyncio
from bot.constants import (SESSION_NAME,SESSION2_NAME,API_ID,API_HASH)
from bot.config import PROXY
from telethon import TelegramClient


# Create a TelegramClient instance (API Bot)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH,proxy=PROXY)

# Create a client instance (User)
client_user = TelegramClient(SESSION2_NAME, API_ID, API_HASH,proxy=PROXY)
