# ---------------------------------------------------
# File Name: settings.py
# Description: /settings panel and /lock, implemented on the Pyrogram bot
#              client so the command no longer depends on the Telethon
#              helper session (which never received the updates reliably).
# ---------------------------------------------------

import os
import re

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID
from devgagan import app
from devgagan.core.func import subscribe
from devgagan.core.get_func import telegram_bot
from devgagan.core.mongo import db as odb

PENDING = {}

PROMPTS = {
    "setchat": (
        "💬 **Set Target Chat**\n\n"
        "Send the numeric chat ID where your files should be sent, "
        "e.g. `-1001234567890`.\n\nSend /settings again to cancel."
    ),
    "setrename": "🏷 **Set Rename Tag**\n\nSend the tag to append to every filename.",
    "setcaption": "📝 **Set Custom Caption**\n\nSend the caption to add under every file.",
    "setreplacement": (
        "🔄 **Word Replacement**\n\n"
        "Send one rule as `'OLD_WORD' 'NEW_WORD'`\n\nExample: `'sample' 'example'`"
    ),
    "delete": (
        "🗑 **Delete Words**\n\n"
        "Send the words (space separated) to remove from captions and filenames."
    ),
    "addsession": "🔑 **Session Login**\n\nSend your Pyrogram V2 session string.",
}

BACK = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="set:back")]])


def _panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Set Chat ID", callback_data="set:setchat"),
         InlineKeyboardButton("Set Rename Tag", callback_data="set:setrename")],
        [InlineKeyboardButton("Caption", callback_data="set:setcaption"),
         InlineKeyboardButton("Replace Words", callback_data="set:setreplacement")],
        [InlineKeyboardButton("Remove Words", callback_data="set:delete"),
         InlineKeyboardButton("Reset All", callback_data="set:reset")],
        [InlineKeyboardButton("Session Login", callback_data="set:addsession"),
         InlineKeyboardButton("Logout", callback_data="set:logout")],
        [InlineKeyboardButton("Set Thumbnail", callback_data="set:setthumb"),
         InlineKeyboardButton("Remove Thumbnail", callback_data="set:remthumb")],
        [InlineKeyboardButton("Upload Method", callback_data="set:uploadmethod")],
    ])


def _upload_keyboard(current):
    pyro = " ✅" if current == "Pyrogram" else ""
    tele = " ✅" if current == "Telethon" else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Pyrogram v2{pyro}", callback_data="set:pyrogram")],
        [InlineKeyboardButton(f"SpyLib v1 ⚡{tele}", callback_data="set:telethon")],
        [InlineKeyboardButton("◀️ Back", callback_data="set:back")],
    ])


async def _panel_text(user_id):
    data = await odb.get_data(user_id)
    chat_id = telegram_bot.user_chat_ids.get(user_id) or (data or {}).get("chat_id")
    rename = telegram_bot.db.get_user_data(user_id, "rename_tag", "Maderauchiha")
    caption = telegram_bot.db.get_user_data(user_id, "custom_caption", "")
    method = telegram_bot.db.get_user_data(user_id, "upload_method", "Pyrogram")
    dest = f"`{chat_id}`" if chat_id else "your DM"
    return (
        "🛠 **Settings**\n\n"
        f"📡 Files go to: {dest}\n"
        f"🏷 Rename tag: {rename}\n"
        f"📝 Caption: {caption or '—'}\n"
        f"📤 Upload method: {method}\n\n"
        "Pick an option below:"
    )


@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    if await subscribe(client, message) == 1:
        return
    PENDING.pop(message.from_user.id, None)
    await message.reply_text(
        await _panel_text(message.from_user.id),
        reply_markup=_panel_keyboard()
    )


@app.on_callback_query(filters.regex(r"^open_settings$"))
async def open_settings_cb(client, query):
    await query.answer()
    await query.message.edit_text(await _panel_text(query.from_user.id), reply_markup=_panel_keyboard())


@app.on_callback_query(filters.regex(r"^set:\w+"))
async def settings_cb(client, query):
    action = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    await query.answer()

    if action == "back":
        await query.message.edit_text(await _panel_text(user_id), reply_markup=_panel_keyboard())
        return

    if action in PROMPTS:
        PENDING[user_id] = action
        await query.message.edit_text(PROMPTS[action], reply_markup=BACK)
        return

    if action == "uploadmethod":
        current = telegram_bot.db.get_user_data(user_id, "upload_method", "Pyrogram")
        await query.message.edit_text("📤 **Choose upload method:**", reply_markup=_upload_keyboard(current))
        return

    if action in ("pyrogram", "telethon"):
        value = "Pyrogram" if action == "pyrogram" else "Telethon"
        telegram_bot.db.save_user_data(user_id, "upload_method", value)
        await query.message.edit_text(f"✅ Upload method set to **{value}**.", reply_markup=_upload_keyboard(value))
        return

    if action == "remthumb":
        thumb = f"{user_id}.jpg"
        if os.path.exists(thumb):
            os.remove(thumb)
            await query.message.edit_text("✅ Thumbnail removed.", reply_markup=_panel_keyboard())
        else:
            await query.message.edit_text("❌ No thumbnail saved.", reply_markup=_panel_keyboard())
        return

    if action == "logout":
        await odb.remove_session(user_id)
        await query.message.edit_text("✅ Logged out — your session was removed.", reply_markup=_panel_keyboard())
        return

    if action == "reset":
        telegram_bot.db.reset_user_data(user_id)
        telegram_bot.user_chat_ids.pop(user_id, None)
        telegram_bot.user_rename_prefs.pop(str(user_id), None)
        telegram_bot.user_caption_prefs.pop(str(user_id), None)
        await odb.remove_channel(user_id)
        thumb = f"{user_id}.jpg"
        if os.path.exists(thumb):
            os.remove(thumb)
        await query.message.edit_text("✅ All settings reset.", reply_markup=_panel_keyboard())
        return


# group=-1 so a pending settings answer is consumed before the t.me link handler
@app.on_message(filters.private, group=-1)
async def settings_input(client, message):
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or user_id not in PENDING:
        return  # nothing pending -> let the normal handlers run

    text = (message.text or "").strip()
    if text.startswith("/"):
        return  # commands pass through; /settings clears the pending step

    step = PENDING.pop(user_id, None)
    if step is None:
        return
    await message.stop_propagation()

    if step == "setchat":
        if not text.lstrip("-").isdigit():
            await message.reply_text("❌ Invalid chat ID. Send a numeric ID like `-1001234567890`.")
            return
        await odb.set_channel(user_id, text)
        telegram_bot.user_chat_ids[user_id] = text
        await message.reply_text(f"✅ Files will now be sent to `{text}`.", reply_markup=_panel_keyboard())
        return

    if step == "setrename":
        telegram_bot.db.save_user_data(user_id, "rename_tag", text)
        telegram_bot.user_rename_prefs[str(user_id)] = text
        await message.reply_text(f"✅ Rename tag set to **{text}**.", reply_markup=_panel_keyboard())
        return

    if step == "setcaption":
        telegram_bot.db.save_user_data(user_id, "custom_caption", text)
        telegram_bot.user_caption_prefs[str(user_id)] = text
        await message.reply_text("✅ Custom caption saved.", reply_markup=_panel_keyboard())
        return

    if step == "setreplacement":
        match = re.match(r"'(.+)' '(.+)'", text)
        if not match:
            await message.reply_text("❌ Invalid format. Use `'OLD_WORD' 'NEW_WORD'`.", reply_markup=BACK)
            return
        old, new = match.groups()
        replacements = telegram_bot.db.get_user_data(user_id, "replacement_words", {}) or {}
        replacements[old] = new
        telegram_bot.db.save_user_data(user_id, "replacement_words", replacements)
        await message.reply_text(f"✅ Saved: **{old}** → **{new}**.", reply_markup=_panel_keyboard())
        return

    if step == "delete":
        words = text.split()
        current = set(telegram_bot.db.get_user_data(user_id, "delete_words", []) or [])
        current.update(words)
        telegram_bot.db.save_user_data(user_id, "delete_words", sorted(current))
        await message.reply_text(
            f"✅ Will be removed: **{', '.join(sorted(current))}**.",
            reply_markup=_panel_keyboard()
        )
        return

    if step == "addsession":
        await odb.set_session(user_id, text)
        await message.reply_text("✅ Session string saved.")
        return

    if step == "setthumb":
        if not message.photo:
            await message.reply_text("❌ Please send a photo.", reply_markup=BACK)
            return
        path = await message.download_media()
        thumb = f"{user_id}.jpg"
        if os.path.exists(thumb):
            os.remove(thumb)
        os.rename(path, thumb)
        await message.reply_text("✅ Thumbnail saved.", reply_markup=_panel_keyboard())
        return


@app.on_message(filters.command("lock") & filters.private)
async def lock_cmd(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    if len(message.command) < 2:
        await message.reply_text("Use: `/lock CHANNEL_ID`")
        return
    try:
        channel_id = int(message.command[1])
    except ValueError:
        await message.reply_text("❌ Invalid channel ID.")
        return
    if telegram_bot.db.lock_channel(channel_id):
        await message.reply_text(f"✅ Channel `{channel_id}` locked.")
    else:
        await message.reply_text(f"❌ Failed to lock `{channel_id}`.")
