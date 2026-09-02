# ---------------------------------------------------
# File Name: __main__.py
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
import importlib
import gc
from pyrogram import idle
from devgagan.modules import ALL_MODULES
from devgagan.core.mongo.plans_db import check_and_remove_expired_users
from aiojobs import create_scheduler

# ----------------------------Bot-Start---------------------------- #

# Function to schedule expiry checks
async def schedule_expiry_check():
    scheduler = await create_scheduler()
    while True:
        await scheduler.spawn(check_and_remove_expired_users())
        await asyncio.sleep(60)  # Check every hour
        gc.collect()

async def devggn_boot():
    # 1) Register every handler BEFORE the clients start, so the dispatcher
    #    picks them all up in one go. One bad module must not kill the bot.
    for all_module in ALL_MODULES:
        try:
            importlib.import_module("devgagan.modules." + all_module)
        except Exception as e:
            print(f"⚠️  Module {all_module} import failed (non-critical): {e}")

    print("""
---------------------------------------------------
📂 Bot Deployed successfully ...
📝 Description: A Pyrogram bot for downloading files from Telegram channels or groups 
                and uploading them back to Telegram.
👨‍💻 Author: Gagan
🌐 GitHub: https://github.com/devgaganin/
📬 Telegram: https://t.me/team_spy_pro
▶️ YouTube: https://youtube.com/@dev_gagan
🗓️ Created: 2025-01-11
🔄 Last Modified: 2025-01-11
🛠️ Version: 2.0.5
📜 License: MIT License
---------------------------------------------------
""")

    # 2) Start the clients (flood-tolerant; raises only after retries run out)
    from devgagan import restrict_bot
    await restrict_bot()

    # 3) Register the command menu on every boot so new commands appear after each deploy
    try:
        from devgagan.modules.start import register_bot_commands
        await register_bot_commands()
    except Exception as e:
        print(f"Command registration failed (non-critical): {e}")

    # 4) One "bot is alive" DM to the owner, throttled across restarts
    try:
        from devgagan import app
        from config import OWNER_ID, ALIVE_COOLDOWN, MONGO_DB
        import datetime
        from motor.motor_asyncio import AsyncIOMotorClient

        now = datetime.datetime.now(datetime.timezone.utc)
        meta_db = AsyncIOMotorClient(MONGO_DB)["telegram_bot"]["bot_meta"]
        doc = await meta_db.find_one({"_id": "alive"})
        last = doc.get("ts") if doc else None
        due = last is None or (now - last).total_seconds() >= ALIVE_COOLDOWN

        if due and OWNER_ID:
            alive_text = (
                "🟢 **Bot is Alive!**\n\n"
                "✅ All systems running normally.\n"
                f"🕐 Started at: `{now.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n\n"
                "🔥 **Your Personal Bot is Ready**"
            )
            await app.send_message(chat_id=OWNER_ID[0], text=alive_text)
            await meta_db.update_one({"_id": "alive"}, {"$set": {"ts": now}}, upsert=True)

    except Exception as e:
        print(f"Startup notification failed (non-critical): {e}")

    # 5) Keep the process alive until a signal stops it
    asyncio.create_task(schedule_expiry_check())
    print("Auto removal started ...")
    await idle()
    print("Bot stopped...")


if __name__ == "__main__":
    # IMPORTANT: Must use the same event loop that __init__.py created and
    # started the Pyrogram/Telethon clients on.  asyncio.run() creates a
    # brand-new loop, making idle() see zero tasks and exit immediately.
    from devgagan import loop
    loop.run_until_complete(devggn_boot())

# ------------------------------------------------------------------ #
