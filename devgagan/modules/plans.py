# ---------------------------------------------------
# File Name: plans.py
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

from datetime import timedelta
import pytz
import datetime, time
from devgagan import app
import asyncio
from config import OWNER_ID
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db  
from pyrogram import filters 
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UserIdInvalid, InputUserDeactivated, UserNotParticipant


async def safe_get_user(client, user_id):
    """Safely fetch a user object; returns None if not found/accessible."""
    try:
        return await client.get_users(user_id)
    except (PeerIdInvalid, UsernameInvalid, UserIdInvalid, InputUserDeactivated):
        return None
    except Exception:
        return None


async def safe_send_message(client, chat_id, text):
    """Safely send a message; silently fails if user blocked bot or not found."""
    try:
        await client.send_message(chat_id=chat_id, text=text)
    except Exception:
        pass


@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric ID.\n\n**Usage:** /rem user_id")
            return

        data = await plans_db.check_premium(user_id)
        if data and data.get("_id"):
            await plans_db.remove_premium(user_id)
            await message.reply_text(f"✅ ᴜꜱᴇʀ `{user_id}` ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !")
            # Try to notify the user — may fail if they never started the bot
            user = await safe_get_user(client, user_id)
            mention = user.mention if user else f"`{user_id}`"
            await safe_send_message(
                client, user_id,
                f"<b>ʜᴇʏ {mention},\n\nʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ.\nᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇ 😊.</b>"
            )
        else:
            await message.reply_text("❌ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜꜱᴇʀ!\nAre you sure this was a premium user ID?")
    else:
        await message.reply_text("**Usage:** /rem user_id")


@app.on_message(filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    user = message.from_user.mention
    data = await plans_db.check_premium(user_id)
    if data and data.get("expire_date"):
        expiry = data.get("expire_date")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")

        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time

        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_left_str = f"{days} ᴅᴀʏꜱ, {hours} ʜᴏᴜʀꜱ, {minutes} ᴍɪɴᴜᴛᴇꜱ"
        await message.reply_text(
            f"⚜️ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :\n\n"
            f"👤 ᴜꜱᴇʀ : {user}\n"
            f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
            f"⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n"
            f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"
        )
    else:
        await message.reply_text(f"ʜᴇʏ {user},\n\nʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs")


@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def get_premium(client, message):
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric ID.")
            return

        data = await plans_db.check_premium(user_id)
        if data and data.get("expire_date"):
            expiry = data.get("expire_date")
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p"
            )
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"

            user = await safe_get_user(client, user_id)
            mention = user.mention if user else f"`{user_id}`"
            await message.reply_text(
                f"⚜️ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :\n\n"
                f"👤 ᴜꜱᴇʀ : {mention}\n"
                f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n"
                f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"
            )
        else:
            await message.reply_text(f"❌ No premium data found for user `{message.command[1]}` in database!")
    else:
        await message.reply_text("**Usage:** /check user_id")


@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def give_premium_cmd_handler(client, message):
    if len(message.command) == 4:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text(
                "❌ Invalid user ID. Please provide a numeric Telegram ID.\n\n"
                "**Usage:** /add user_id 1 day"
            )
            return

        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p")
        duration = message.command[2] + " " + message.command[3]
        seconds = await get_seconds(duration)

        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            await plans_db.add_premium(user_id, expiry_time)
            data = await plans_db.check_premium(user_id)
            expiry = data.get("expire_date")
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p"
            )

            # Try to fetch user info — may not be possible for users who never messaged the bot
            user = await safe_get_user(client, user_id)
            mention = user.mention if user else f"`{user_id}`"

            await message.reply_text(
                f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅\n\n"
                f"👤 ᴜꜱᴇʀ : {mention}\n"
                f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{duration}</code>\n\n"
                f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}\n\n"
                f"__**Powered by Maderauchiha__**",
                disable_web_page_preview=True
            )
            # Notify the user if possible
            await safe_send_message(
                client, user_id,
                f"👋 ʜᴇʏ {mention},\n"
                f"ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ.\n"
                f"ᴇɴᴊᴏʏ !! ✨🎉\n\n"
                f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{duration}</code>\n"
                f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}"
            )
        else:
            await message.reply_text(
                "❌ Invalid time format.\n\n"
                "**Examples:**\n"
                "• `/add 123456789 1 hour` or `2 hours`\n"
                "• `/add 123456789 1 day` or `7 days`\n"
                "• `/add 123456789 1 month` or `3 months`\n"
                "• `/add 123456789 1 year`\n"
                "• `/add 123456789 30 min` or `90 minutes`"
            )
    else:
        await message.reply_text(
            "**Usage:** `/add user_id time unit`\n\n"
            "**Examples:**\n"
            "• `/add 123456789 1 hour`\n"
            "• `/add 123456789 12 hours`\n"
            "• `/add 123456789 1 day`\n"
            "• `/add 123456789 30 days`\n"
            "• `/add 123456789 1 month`\n"
            "• `/add 123456789 3 months`\n"
            "• `/add 123456789 1 year`\n\n"
            "💡 Both singular and plural units work (hour/hours, day/days, etc.)"
        )


@app.on_message(filters.command("transfer"))
async def transfer_premium(client, message):
    if len(message.command) == 2:
        try:
            new_user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric Telegram ID.")
            return

        sender_user_id = message.from_user.id
        sender_user = await safe_get_user(client, sender_user_id)
        new_user = await safe_get_user(client, new_user_id)

        sender_mention = sender_user.mention if sender_user else f"`{sender_user_id}`"
        new_mention = new_user.mention if new_user else f"`{new_user_id}`"

        data = await plans_db.check_premium(sender_user_id)

        if data and data.get("_id"):
            expiry = data.get("expire_date")
            await plans_db.remove_premium(sender_user_id)
            await plans_db.add_premium(new_user_id, expiry)

            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p"
            )
            time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            current_time = time_zone.strftime("%d-%m-%Y\n⏱️ **Transfer Time:** %I:%M:%S %p")

            await message.reply_text(
                f"✅ **Premium Plan Transferred Successfully!**\n\n"
                f"👤 **From:** {sender_mention}\n"
                f"👤 **To:** {new_mention}\n"
                f"⏳ **Expiry Date:** {expiry_str_in_ist}\n\n"
                f"__Powered by Maderauchiha__ 🚀"
            )
            await safe_send_message(
                client, new_user_id,
                f"👋 **Hey {new_mention},**\n\n"
                f"🎉 **Your Premium Plan has been Transferred!**\n"
                f"🛡️ **Transferred From:** {sender_mention}\n\n"
                f"⏳ **Expiry Date:** {expiry_str_in_ist}\n"
                f"📅 **Transferred On:** {current_time}\n\n"
                f"__Enjoy the Service!__ ✨"
            )
        else:
            await message.reply_text(
                "⚠️ **You are not a Premium user!**\n\nOnly Premium users can transfer their plans."
            )
    else:
        await message.reply_text("⚠️ **Usage:** /transfer user_id\n\nReplace `user_id` with the new user's ID.")


async def premium_remover():
    all_users = await plans_db.premium_users()
    removed_users = []
    not_removed_users = []

    for user_id in all_users:
        try:
            user = await app.get_users(user_id)
            chk_time = await plans_db.check_premium(user_id)

            if chk_time and chk_time.get("expire_date"):
                expiry_date = chk_time["expire_date"]
                if expiry_date <= datetime.datetime.now():
                    name = user.first_name
                    await plans_db.remove_premium(user_id)
                    await safe_send_message(app, user_id, f"Hello {name}, your premium subscription has expired.")
                    print(f"{name}, your premium subscription has expired.")
                    removed_users.append(f"{name} ({user_id})")
                else:
                    name = user.first_name
                    current_time = datetime.datetime.now()
                    time_left = expiry_date - current_time
                    days = time_left.days
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if days > 0:
                        remaining_time = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
                    elif hours > 0:
                        remaining_time = f"{hours} hours, {minutes} minutes, {seconds} seconds"
                    elif minutes > 0:
                        remaining_time = f"{minutes} minutes, {seconds} seconds"
                    else:
                        remaining_time = f"{seconds} seconds"
                    print(f"{name} : Remaining Time : {remaining_time}")
                    not_removed_users.append(f"{name} ({user_id})")
        except Exception:
            await plans_db.remove_premium(user_id)
            print(f"Unknown users captured : {user_id} removed")
            removed_users.append(f"Unknown ({user_id})")

    return removed_users, not_removed_users


@app.on_message(filters.command("freez") & filters.user(OWNER_ID))
async def refresh_users(_, message):
    removed_users, not_removed_users = await premium_remover()
    removed_text = "\n".join(removed_users) if removed_users else "No users removed."
    not_removed_text = "\n".join(not_removed_users) if not_removed_users else "No users remaining with premium."
    summary = (
        f"**Here is Summary...**\n\n"
        f"> **Removed Users:**\n{removed_text}\n\n"
        f"> **Not Removed Users:**\n{not_removed_text}"
    )
    await message.reply(summary)
