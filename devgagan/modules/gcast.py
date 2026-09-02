# ---------------------------------------------------
# File Name: gcast.py
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
import traceback
from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from config import OWNER_ID
from devgagan import app
from devgagan.core.mongo.users_db import get_users

async def send_msg(user_id, message):
    """Send a message to a user with error handling"""
    try:
        x = await message.copy(chat_id=user_id)
        return True, f"✅ {user_id}"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return False, f"❌ {user_id} : Deactivated Account"
    except UserIsBlocked:
        return False, f"❌ {user_id} : Blocked Bot"
    except PeerIdInvalid:
        return False, f"❌ {user_id} : Invalid User ID"
    except Exception as e:
        return False, f"❌ {user_id} : {str(e)[:50]}"


@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, message):
    """🔊 Broadcast message to all users"""
    if not message.reply_to_message:
        await message.reply_text(
            "📨 **Broadcast Message Guide**\n\n"
            "તમને broadcast કરવું હોય તો:\n"
            "1. એક message reply કરો\n"
            "2. `/broadcast` command ટાઈપ કરો\n\n"
            "Example: તમે કોઈ message reply કરીને `/broadcast` લખો"
        )
        return    
    
    exmsg = await message.reply_text("⏳ **Broadcast શરૂ કર્યું...**\n\nમોટી થોડા સમય લાગશે...")
    all_users = (await get_users()) or []
    done_users = 0
    failed_users = 0
    failed_list = []
    
    if not all_users:
        await exmsg.edit_text("❌ કોઈ users નથી broadcast કરવા માટે.")
        return
    
    for user in all_users:
        try:
            success, msg = await send_msg(user, message.reply_to_message)
            if success:
                done_users += 1
            else:
                failed_users += 1
                failed_list.append(msg)
            await asyncio.sleep(0.1)  # Avoid flood
        except Exception as e:
            failed_users += 1
            failed_list.append(f"❌ {user} : {str(e)[:30]}")
    
    # Send final report
    if failed_users == 0:
        await exmsg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"📤 Total Users: `{done_users}`\n"
            f"✅ Success: `{done_users}`\n"
            f"❌ Failed: `0`"
        )
    else:
        await exmsg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"📤 Total Users: `{done_users + failed_users}`\n"
            f"✅ Success: `{done_users}`\n"
            f"❌ Failed: `{failed_users}`"
        )


@app.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def gcast_broadcast(_, message):
    """📢 Group broadcast - Send message to all groups where bot is active (ALTERNATIVE)"""
    if not message.reply_to_message:
        await message.reply_text(
            "📢 **Group Broadcast Guide**\n\n"
            "તમને group broadcast કરવું હોય તો:\n"
            "1. એક message reply કરો\n"
            "2. `/gcast` command ટાઈપ કરો\n\n"
            "આ તમામ users ને message મોકલશે."
        )
        return    
    
    exmsg = await message.reply_text("⏳ **Broadcasting શરૂ કર્યું...**")
    all_users = (await get_users()) or []
    done_users = 0
    failed_users = 0
    
    for user in all_users:
        try:
            success, msg = await send_msg(user, message.reply_to_message)
            if success:
                done_users += 1
            else:
                failed_users += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed_users += 1
    
    if failed_users == 0:
        await exmsg.edit_text(
            f"✅ **Group Broadcast Success!**\n\n"
            f"📤 Message sent to `{done_users}` users"
        )
    else:
        await exmsg.edit_text(
            f"✅ **Group Broadcast Complete!**\n\n"
            f"✅ Success: `{done_users}`\n"
            f"❌ Failed: `{failed_users}`"
        )


