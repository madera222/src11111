# ---------------------------------------------------
# File Name: __init__.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait as PyroFloodWait
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon import TelegramClient          # async version (not telethon.sync)
from telethon.errors import FloodWaitError as TelethonFloodWait
from motor.motor_asyncio import AsyncIOMotorClient

# ── Event loop ────────────────────────────────────────────────────────────────
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

BOT_ID = None
BOT_NAME = ""
BOT_USERNAME = ""

# ── Pyrogram clients ──────────────────────────────────────────────────────────
app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=200,
    parse_mode=ParseMode.MARKDOWN
)

if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = None

# ── Telethon clients (async-friendly – started inside restrict_bot) ───────────
sex = TelegramClient("sexrepo", API_ID, API_HASH)

# ── MongoDB setup ─────────────────────────────────────────────────────────────
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]


async def create_ttl_index():
    """Ensure the TTL index exists for the tokens collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)


async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")


async def _start_with_flood_retry(start_coro, label, attempts=5):
    """Telegram answers repeated bot auths with FLOOD_WAIT_X. Exiting makes the
    host restart us and the next attempt lands inside the same window, extending
    it — so we wait the required time in-process and retry instead."""
    for i in range(1, attempts + 1):
        try:
            await start_coro()
            print(f"✅ {label} started")
            return True
        except (PyroFloodWait, TelethonFloodWait) as e:
            wait = int(getattr(e, "value", None) or getattr(e, "seconds", None) or 60) + 10
            print(f"⏳ {label}: Telegram FLOOD_WAIT — {wait}s રાહ જોઈએ છીએ (પ્રયાસ {i}/{attempts})")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"⚠️  {label} start failed (non-critical): {e}")
            return False
    print(f"❌ {label}: {attempts} પ્રયાસ પછી પણ start ન થયું.")
    return False


async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME

    await setup_database()

    # Start the Pyrogram bot first; only after retries are exhausted do we give up
    if not await _start_with_flood_retry(app.start, "Pyrogram bot", attempts=5):
        raise RuntimeError("Pyrogram bot authorize ન થઈ શક્યું — ઉપરના FLOOD_WAIT/error logs જુઓ")

    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    print(f"✅ Pyrogram bot started: @{BOT_USERNAME}")

    # Telethon helper authorizes the same bot token; starting it together with the
    # Pyrogram bot doubles the auth pressure, so only start it after the bot is live.
    await asyncio.sleep(5)
    await _start_with_flood_retry(lambda: sex.start(bot_token=BOT_TOKEN), "Telethon sexrepo helper", attempts=3)

    if pro:
        try:
            await pro.start()
            print("✅ Pro (STRING) client started")
        except Exception as e:
            print(f"⚠️  Pro client start failed (non-critical): {e}")

    if userrbot:
        try:
            await userrbot.start()
            print("✅ Userrbot (DEFAULT_SESSION) client started")
        except Exception as e:
            print(f"⚠️  Userrbot start failed (non-critical): {e}")
