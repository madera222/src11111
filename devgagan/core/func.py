# ---------------------------------------------------
# File Name: func.py
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

import math
import time , re
from pyrogram import enums
from config import CHANNEL_ID, OWNER_ID, FORCE_JOIN_URL
from devgagan.core.mongo.plans_db import premium_users
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import cv2
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant, UserNotParticipant
from datetime import datetime as dt
import asyncio, subprocess, re, os, time
async def chk_user(message, user_id):
    user = await premium_users()
    if user_id in user or user_id in OWNER_ID:
        return 0
    else:
        return 1
async def gen_link(app, chat_id):
    try:
        link = await app.export_chat_invite_link(chat_id)
        return link
    except Exception:
        return None

async def force_join_markup(client):
    if not CHANNEL_ID:
        return None
    url = FORCE_JOIN_URL or await gen_link(client, CHANNEL_ID)
    if not url:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel ✅", url=url)]])


async def subscribe(app, message):
    update_channel = CHANNEL_ID
    if not update_channel:
        return 0

    try:
        user = await app.get_chat_member(update_channel, message.from_user.id)
        if str(user.status) in ("ChatMemberStatus.BANNED", "kicked"):
            await message.reply_text("You are banned from this bot's channel. Contact the owner.")
            return 1
        return 0
    except UserNotParticipant:
        # Text + button only: an external photo URL here could fail and, because we are
        # inside an except block, that failure would escape and kill the caller's handler.
        try:
            markup = await force_join_markup(app)
            caption = (
                "🔒 **Channel Join કરવું પડશે**\n\n"
                "આ bot વાપરવા માટે અમારી channel join કરો, પછી ફરી /start મોકલો."
            )
            if markup:
                await message.reply_text(caption, reply_markup=markup)
            else:
                await message.reply_text(caption)
        except Exception as e:
            print(f"Force-join prompt failed: {e}")
        return 1
    except Exception as e:
        print(f"Force-join check failed (is the bot admin in CHANNEL_ID?): {e}")
        return 0
async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        # Normalize: lowercase, strip spaces, remove trailing 's' to handle plurals
        raw_unit = ts[index:].strip().lower()
        # Strip trailing 's' only when it makes the unit singular (e.g. "hours"→"hour")
        # But not for "s" alone (seconds shorthand)
        if len(raw_unit) > 1 and raw_unit.endswith('s'):
            unit = raw_unit[:-1]  # hours→hour, days→day, months→month, years→year, mins→min
        else:
            unit = raw_unit

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    # Seconds
    if unit in ('s', 'sec', 'second'):
        return value
    # Minutes
    elif unit in ('min', 'minute', 'm'):
        return value * 60
    # Hours
    elif unit in ('hour', 'hr', 'h'):
        return value * 3600
    # Days
    elif unit in ('day', 'd'):
        return value * 86400
    # Weeks
    elif unit in ('week', 'wk', 'w'):
        return value * 86400 * 7
    # Months
    elif unit in ('month', 'mo'):
        return value * 86400 * 30
    # Years
    elif unit in ('year', 'yr', 'y'):
        return value * 86400 * 365
    else:
        return 0
PROGRESS_BAR = """\n
│ **__Completed:__** {1}/{2}
│ **__Bytes:__** {0}%
│ **__Speed:__** {3}/s
│ **__ETA:__** {4}
╰─────────────────────╯
"""
async def progress_bar(current, total, ud_type, message, start):

    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:

        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["♦" for i in range(math.floor(percentage / 10))]),
            ''.join(["◇" for i in range(10 - math.floor(percentage / 10))]))

        tmp = progress + PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),

            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n│ {}".format(ud_type, tmp),)             
        except:
            pass

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2] 
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)
async def userbot_join(userbot, invite_link):
    try:
        await userbot.join_chat(invite_link)
        return "Successfully joined the Channel"
    except UserAlreadyParticipant:
        return "User is already a participant."
    except (InviteHashInvalid, InviteHashExpired):
        return "Could not join. Maybe your link is expired or Invalid."
    except FloodWait:
        return "Too many requests, try again later."
    except Exception as e:
        print(e)
        return "Could not join, try joining manually."
def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)   
    try:
        link = [x[0] for x in url][0]
        if link:
            return link
        else:
            return False
    except Exception:
        return False
def video_metadata(file):
    default_values = {'width': 1, 'height': 1, 'duration': 1}
    try:
        vcap = cv2.VideoCapture(file)
        if not vcap.isOpened():
            return default_values  

        width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0:
            return default_values  

        duration = round(frame_count / fps)
        if duration <= 0:
            return default_values  

        vcap.release()
        return {'width': width, 'height': height, 'duration': duration}

    except Exception as e:
        print(f"Error in video_metadata: {e}")
        return default_values

def hhmmss(seconds):
    return time.strftime('%H:%M:%S',time.gmtime(seconds))

async def screenshot(video, duration, sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    time_stamp = hhmmss(int(duration)/2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg",
           "-ss",
           f"{time_stamp}", 
           "-i",
           f"{video}",
           "-frames:v",
           "1", 
           f"{out}",
           "-y"
          ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    if os.path.isfile(out):
        return out
    else:
        None  
last_update_time = time.time()
async def progress_callback(current, total, progress_message):
    percent = (current / total) * 100
    global last_update_time
    current_time = time.time()

    if current_time - last_update_time >= 10 or percent % 10 == 0:
        completed_blocks = int(percent // 10)
        remaining_blocks = 10 - completed_blocks
        progress_bar = "♦" * completed_blocks + "◇" * remaining_blocks
        current_mb = current / (1024 * 1024)  
        total_mb = total / (1024 * 1024)      
        await progress_message.edit(
    f"╭──────────────────╮\n"
    f"│        **__Uploading...__**       \n"
    f"├──────────\n"
    f"│ {progress_bar}\n\n"
    f"│ **__Progress:__** {percent:.2f}%\n"
    f"│ **__Uploaded:__** {current_mb:.2f} MB / {total_mb:.2f} MB\n"
    f"╰──────────────────╯\n\n"
    f"**__Powered by Maderauchiha__**"
        )

        last_update_time = current_time
async def prog_bar(current, total, ud_type, message, start):

    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:

        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["♦" for i in range(math.floor(percentage / 10))]),
            ''.join(["◇" for i in range(10 - math.floor(percentage / 10))]))

        tmp = progress + PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),

            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit_text(
                text="{}\n│ {}".format(ud_type, tmp),)             

        except:
            pass
