# ---------------------------------------------------
# File Name: get_func.py
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
import os
import re
import time
import gc
from typing import Dict, Set, Optional, Union, Any, Tuple, List
from pathlib import Path
from functools import lru_cache, wraps
from collections import defaultdict
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import aiofiles
import pymongo
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, RPCError
from pyrogram.enums import MessageMediaType, ParseMode
from telethon.tl.types import DocumentAttributeVideo
from telethon import events, Button
from devgagan import app, sex as gf
from devgagan.core.func import *
from devgagan.core.mongo import db as odb
from devgagantools import fast_upload
from config import MONGO_DB as MONGODB_CONNECTION_STRING, LOG_GROUP, OWNER_ID, STRING, API_ID, API_HASH

# Import pro userbot if STRING is available
if STRING:
    from devgagan import pro
else:
    pro = None


async def log_copy(message):
    """Mirror a delivered message into the owner log; never fail the user's delivery."""
    if not LOG_GROUP:
        return
    try:
        await message.copy(LOG_GROUP)
    except Exception as e:
        print(f"Owner log copy failed (non-critical): {e}")


async def safe_log(text):
    """Report an error to the owner log without ever raising — a bad LOG_GROUP
    must not turn an error report into a second crash."""
    print(text)
    try:
        if LOG_GROUP:
            await app.send_message(LOG_GROUP, text)
    except Exception as e:
        print(f"safe_log failed (non-critical): {e}")

# Constants and Configuration
@dataclass
class BotConfig:
    DB_NAME: str = "smart_users"
    COLLECTION_NAME: str = "super_user"
    VIDEO_EXTS: Set[str] = field(default_factory=lambda: {
        'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm', 'mpg', 'mpeg', 
        '3gp', 'ts', 'm4v', 'f4v', 'vob'
    })
    DOC_EXTS: Set[str] = field(default_factory=lambda: {
        'pdf', 'docx', 'txt', 'epub', 'docs'
    })
    IMG_EXTS: Set[str] = field(default_factory=lambda: {
        'jpg', 'jpeg', 'png', 'webp'
    })
    AUDIO_EXTS: Set[str] = field(default_factory=lambda: {
        'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'
    })
    SIZE_LIMIT: int = 2 * 1024**3  # 2GB
    PART_SIZE: int = int(1.9 * 1024**3)  # 1.9GB for splitting

@dataclass
class UserProgress:
    previous_done: int = 0
    previous_time: float = field(default_factory=time.time)

class DatabaseManager:
    """Enhanced database operations with error handling and caching"""
    def __init__(self, connection_string: str, db_name: str, collection_name: str):
        self.client = pymongo.MongoClient(connection_string)
        self.collection = self.client[db_name][collection_name]
        self._cache = {}
    
    def get_user_data(self, user_id: int, key: str, default=None) -> Any:
        cache_key = f"{user_id}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            doc = self.collection.find_one({"_id": user_id})
            value = doc.get(key, default) if doc else default
            self._cache[cache_key] = value
            return value
        except Exception as e:
            print(f"Database read error: {e}")
            return default
    
    def save_user_data(self, user_id: int, key: str, value: Any) -> bool:
        cache_key = f"{user_id}:{key}"
        try:
            self.collection.update_one(
                {"_id": user_id}, 
                {"$set": {key: value}}, 
                upsert=True
            )
            self._cache[cache_key] = value
            return True
        except Exception as e:
            print(f"Database save error for {key}: {e}")
            return False
    
    def clear_user_cache(self, user_id: int):
        """Clear cache for specific user"""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self._cache[key]
    
    def get_protected_channels(self) -> Set[int]:
        try:
            return {doc["channel_id"] for doc in self.collection.find({"channel_id": {"$exists": True}})}
        except:
            return set()
    
    def lock_channel(self, channel_id: int) -> bool:
        try:
            self.collection.insert_one({"channel_id": channel_id})
            return True
        except:
            return False
    
    def reset_user_data(self, user_id: int) -> bool:
        try:
            self.collection.update_one(
                {"_id": user_id}, 
                {"$unset": {
                    "delete_words": "", "replacement_words": "", 
                    "watermark_text": "", "duration_limit": "",
                    "custom_caption": "", "rename_tag": ""
                }}
            )
            self.clear_user_cache(user_id)
            return True
        except Exception as e:
            print(f"Reset error: {e}")
            return False

class MediaProcessor:
    """Advanced media processing and file type detection"""
    def __init__(self, config: BotConfig):
        self.config = config
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type based on extension"""
        ext = Path(filename).suffix.lower().lstrip('.')
        if ext in self.config.VIDEO_EXTS:
            return 'video'
        elif ext in self.config.IMG_EXTS:
            return 'photo'
        elif ext in self.config.AUDIO_EXTS:
            return 'audio'
        elif ext in self.config.DOC_EXTS:
            return 'document'
        return 'document'
    
    @staticmethod
    def get_media_info(msg) -> Tuple[Optional[str], Optional[int], str]:
        """Extract filename, file size, and media type from message"""
        if msg.document:
            return msg.document.file_name or "document", msg.document.file_size, "document"
        elif msg.video:
            return msg.video.file_name or "video.mp4", msg.video.file_size, "video"
        elif msg.photo:
            return "photo.jpg", msg.photo.file_size, "photo"
        elif msg.audio:
            return msg.audio.file_name or "audio.mp3", msg.audio.file_size, "audio"
        elif msg.voice:
            return "voice.ogg", getattr(msg.voice, 'file_size', 1), "voice"
        elif msg.video_note:
            return "video_note.mp4", getattr(msg.video_note, 'file_size', 1), "video_note"
        elif msg.sticker:
            return "sticker.webp", getattr(msg.sticker, 'file_size', 1), "sticker"
        return "unknown", 1, "document"

class ProgressManager:
    """Enhanced progress tracking with better formatting"""
    def __init__(self):
        self.user_progress: Dict[int, UserProgress] = defaultdict(UserProgress)
        self._last_edit: Dict[int, float] = {}
    
    def calculate_progress(self, done: int, total: int, user_id: int, uploader: str = "SpyLib") -> str:
        now = time.time()
        # Throttle: only update every 5 seconds to avoid API flood and speed up uploads
        last = self._last_edit.get(user_id, 0)
        if done != total and (now - last) < 5:
            return None  # Skip this update
        self._last_edit[user_id] = now

        user_data = self.user_progress[user_id]
        percent = (done / total) * 100
        progress_bar = "♦" * int(percent // 10) + "◇" * (10 - int(percent // 10))
        done_mb, total_mb = done / (1024**2), total / (1024**2)
        
        # Calculate speed and ETA
        speed = max(0, done - user_data.previous_done)
        elapsed_time = max(0.1, time.time() - user_data.previous_time)
        speed_mbps = (speed * 8) / (1024**2 * elapsed_time) if elapsed_time > 0 else 0
        eta_seconds = ((total - done) / speed) if speed > 0 else 0
        eta_min = eta_seconds / 60
        
        # Update progress
        user_data.previous_done = done
        user_data.previous_time = time.time()
        
        return (
            f"╭──────────────────╮\n"
            f"│     **__{uploader} ⚡ Uploader__**\n"
            f"├──────────\n"
            f"│ {progress_bar}\n\n"
            f"│ **__Progress:__** {percent:.2f}%\n"
            f"│ **__Done:__** {done_mb:.2f} MB / {total_mb:.2f} MB\n"
            f"│ **__Speed:__** {speed_mbps:.2f} Mbps\n"
            f"│ **__ETA:__** {eta_min:.2f} min\n"
            f"╰──────────────────╯\n\n"
            f"**__Powered by Maderauchiha__**"
        )

class CaptionFormatter:
    """Advanced caption processing with markdown to HTML conversion"""
    
    @staticmethod
    async def markdown_to_html(caption: str) -> str:
        """Convert markdown formatting to HTML"""
        if not caption:
            return ""
        
        replacements = [
            (r"^> (.*)", r"<blockquote>\1</blockquote>"),
            (r"```(.*?)```", r"<pre>\1</pre>"),
            (r"`(.*?)`", r"<code>\1</code>"),
            (r"\*\*(.*?)\*\*", r"<b>\1</b>"),
            (r"\*(.*?)\*", r"<b>\1</b>"),
            (r"__(.*?)__", r"<i>\1</i>"),
            (r"_(.*?)_", r"<i>\1</i>"),
            (r"~~(.*?)~~", r"<s>\1</s>"),
            (r"\|\|(.*?)\|\|", r"<details>\1</details>"),
            (r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>')
        ]
        
        result = caption
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.MULTILINE | re.DOTALL)
        
        return result.strip()

class FileOperations:
    """File operations with enhanced error handling"""
    def __init__(self, config: BotConfig, db: DatabaseManager):
        self.config = config
        self.db = db
    
    @asynccontextmanager
    async def safe_file_operation(self, file_path: str):
        """Safe file operations with automatic cleanup"""
        try:
            yield file_path
        finally:
            await self._cleanup_file(file_path)
    
    async def _cleanup_file(self, file_path: str):
        """Safely remove file"""
        if file_path and os.path.exists(file_path):
            try:
                await asyncio.to_thread(os.remove, file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
    
    async def process_filename(self, file_path: str, user_id: int) -> str:
        """Process filename with user preferences"""
        delete_words = set(self.db.get_user_data(user_id, "delete_words", []))
        replacements = self.db.get_user_data(user_id, "replacement_words", {})
        rename_tag = self.db.get_user_data(user_id, "rename_tag", "Maderauchiha")
        
        path = Path(file_path)
        name = path.stem
        extension = path.suffix.lstrip('.')
        
        # Process filename
        for word in delete_words:
            name = name.replace(word, "")
        
        for word, replacement in replacements.items():
            name = name.replace(word, replacement)
        
        # Normalize extension for videos
        if extension.lower() in self.config.VIDEO_EXTS and extension.lower() not in ['mp4']:
            extension = 'mp4'
        
        new_name = f"{name.strip()} {rename_tag}.{extension}"
        new_path = path.parent / new_name
        
        await asyncio.to_thread(os.rename, file_path, new_path)
        return str(new_path)
    
    async def split_large_file(self, file_path: str, app_client, sender: int, target_chat_id: int, caption: str, topic_id: Optional[int] = None):
        """Split large files into smaller parts"""
        if not os.path.exists(file_path):
            await app_client.send_message(sender, "❌ File not found!")
            return

        file_size = os.path.getsize(file_path)
        start_msg = await app_client.send_message(
            sender, f"ℹ️ File size: {file_size / (1024**2):.2f} MB\n🔄 Splitting and uploading..."
        )

        part_number = 0
        base_path = Path(file_path)
        
        try:
            async with aiofiles.open(file_path, mode="rb") as f:
                while True:
                    chunk = await f.read(self.config.PART_SIZE)
                    if not chunk:
                        break

                    part_file = f"{base_path.stem}.part{str(part_number).zfill(3)}{base_path.suffix}"

                    async with aiofiles.open(part_file, mode="wb") as part_f:
                        await part_f.write(chunk)

                    part_caption = f"{caption}\n\n**Part: {part_number + 1}**" if caption else f"**Part: {part_number + 1}**"
                    
                    edit_msg = await app_client.send_message(target_chat_id, f"⬆️ Uploading part {part_number + 1}...")
                    
                    try:
                        result = await app_client.send_document(
                            target_chat_id,
                            document=part_file,
                            caption=part_caption,
                            reply_to_message_id=topic_id,
                            progress=progress_bar,
                            progress_args=("╭──────────────╮\n│ **__Pyro Uploader__**\n├────────", edit_msg, time.time())
                        )
                        await log_copy(result)
                        await edit_msg.delete()
                    finally:
                        if os.path.exists(part_file):
                            os.remove(part_file)
                    
                    part_number += 1

        finally:
            await start_msg.delete()
            if os.path.exists(file_path):
                os.remove(file_path)

class SmartTelegramBot:
    """Main bot class with all functionality"""
    def __init__(self):
        self.config = BotConfig()
        self.db = DatabaseManager(MONGODB_CONNECTION_STRING, self.config.DB_NAME, self.config.COLLECTION_NAME)
        self.media_processor = MediaProcessor(self.config)
        self.progress_manager = ProgressManager()
        self.file_ops = FileOperations(self.config, self.db)
        self.caption_formatter = CaptionFormatter()
        
        # User session management
        self.user_sessions: Dict[int, str] = {}
        self.pending_photos: Set[int] = set()
        self.user_chat_ids: Dict[int, str] = {}
        self.user_rename_prefs: Dict[str, str] = {}
        self.user_caption_prefs: Dict[str, str] = {}
        
        # Pro userbot reference
        self.pro_client = pro
        print(f"Pro client available: {'Yes' if self.pro_client else 'No'}")
    
    def get_thumbnail_path(self, user_id: int) -> Optional[str]:
        """Get user's custom thumbnail path"""
        thumb_path = f'{user_id}.jpg'
        return thumb_path if os.path.exists(thumb_path) else None
    
    def parse_target_chat(self, target: str) -> Tuple[int, Optional[int]]:
        """Parse chat ID and topic ID from target string"""
        if '/' in target:
            parts = target.split('/')
            return int(parts[0]), int(parts[1])
        return int(target), None
    
    async def process_user_caption(self, original_caption: str, user_id: int) -> str:
        """Process caption with user preferences"""
        custom_caption = self.user_caption_prefs.get(str(user_id), "") or self.db.get_user_data(user_id, "custom_caption", "")
        delete_words = set(self.db.get_user_data(user_id, "delete_words", []))
        replacements = self.db.get_user_data(user_id, "replacement_words", {})
        
        # Process original caption
        processed = original_caption or ""
        
        # Remove delete words
        for word in delete_words:
            processed = processed.replace(word, "")
        
        # Apply replacements
        for word, replacement in replacements.items():
            processed = processed.replace(word, replacement)
        
        # Add custom caption
        if custom_caption:
            processed = f"{processed}\n\n{custom_caption}".strip()
        
        return processed if processed else None

    async def upload_with_pyrogram(self, file_path: str, user_id: int, target_chat_id: int, caption: str, topic_id: Optional[int] = None, edit_msg=None):
        """Upload using Pyrogram with proper file type detection"""
        file_type = self.media_processor.get_file_type(file_path)
        thumb_path = self.get_thumbnail_path(user_id)
        
        progress_args = ("╭──────────────╮\n│ **__Pyro Uploader__**\n├────────", edit_msg, time.time())
        
        try:
            if file_type == 'video':
                # Get video metadata
                metadata = {}
                if 'video_metadata' in globals():
                    metadata = video_metadata(file_path)
                
                width = metadata.get('width', 0)
                height = metadata.get('height', 0)
                duration = metadata.get('duration', 0)
                
                # Generate thumbnail if not exists
                if not thumb_path and 'screenshot' in globals():
                    try:
                        thumb_path = await screenshot(file_path, duration, user_id)
                    except:
                        pass
                
                result = await app.send_video(
                    chat_id=target_chat_id,
                    video=file_path,
                    caption=caption,
                    height=height,
                    width=width,
                    duration=duration,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=progress_args
                )
                
            elif file_type == 'photo':
                result = await app.send_photo(
                    chat_id=target_chat_id,
                    photo=file_path,
                    caption=caption,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=progress_args
                )
                
            elif file_type == 'audio':
                result = await app.send_audio(
                    chat_id=target_chat_id,
                    audio=file_path,
                    caption=caption,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=progress_args
                )
                
            else:  # document
                result = await app.send_document(
                    chat_id=target_chat_id,
                    document=file_path,
                    caption=caption,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=progress_args
                )
            
            # Copy to log group
            await log_copy(result)
            if edit_msg:
                try:
                    await edit_msg.delete()
                except Exception:
                    pass
            return result
            
        except Exception as e:
            await safe_log(f"**Pyrogram Upload Failed:** {str(e)}")
            try:
                if edit_msg:
                    await edit_msg.edit(
                        f"❌ **Upload failed.**\n\n"
                        f"Target chat `{target_chat_id}` પર bot મોકલી શક્યું નહીં.\n"
                        f"Bot એ channel માં admin છે કે નહીં ચેક કરો. `/removechannel` થી DM પર પાછા આવી શકો છો.\n\n"
                        f"Error: `{type(e).__name__}: {str(e)[:200]}`"
                    )
                else:
                    await app.send_message(user_id, f"❌ Upload failed: `{type(e).__name__}: {str(e)[:200]}`")
            except Exception:
                pass
            return None

    async def upload_with_telethon(self, file_path: str, user_id: int, target_chat_id: int, caption: str, topic_id: Optional[int] = None, edit_msg=None):
        """Upload using Telethon (SpyLib) with enhanced features"""
        try:
            if edit_msg:
                await edit_msg.delete()
            
            progress_message = await gf.send_message(user_id, "**__SpyLib ⚡ Uploading...__**")
            html_caption = await self.caption_formatter.markdown_to_html(caption)
            
            # Upload file using fast_upload
            uploaded = await fast_upload(
                gf, file_path,
                reply=progress_message,
                name=None,
                progress_bar_function=lambda done, total: self.progress_manager.calculate_progress(done, total, user_id, "SpyLib"),
                user_id=user_id
            )
            
            await progress_message.delete()
            
            # Prepare attributes based on file type
            attributes = []
            file_type = self.media_processor.get_file_type(file_path)
            
            if file_type == 'video':
                if 'video_metadata' in globals():
                    metadata = video_metadata(file_path)
                    duration = metadata.get('duration', 0)
                    width = metadata.get('width', 0)
                    height = metadata.get('height', 0)
                    attributes = [DocumentAttributeVideo(
                        duration=duration, w=width, h=height, supports_streaming=True
                    )]
            
            thumb_path = self.get_thumbnail_path(user_id)
            
            # Send to target chat
            sent = await gf.send_file(
                target_chat_id,
                uploaded,
                caption=html_caption,
                attributes=attributes,
                reply_to=topic_id,
                parse_mode='html',
                thumb=thumb_path
            )
            
            if LOG_GROUP:
                try:
                    await sent.copy_to(LOG_GROUP)
                except Exception as e:
                    print(f"Owner log copy failed (non-critical): {e}")
            
        except Exception as e:
            await safe_log(f"**SpyLib Upload Failed:** {str(e)}")
            try:
                await gf.send_message(user_id, f"❌ Upload failed: `{type(e).__name__}: {str(e)[:200]}`")
            except Exception:
                pass
            return None

    async def handle_large_file_upload(self, file_path: str, sender: int, edit_msg, caption: str):
        """Handle files larger than 2GB using pro client"""
        if not self.pro_client:
            await edit_msg.edit('**❌ 4GB upload not available - Pro client not configured**')
            return

        await edit_msg.edit('**✅ 4GB upload starting...**')
        
        target_chat_str = self.user_chat_ids.get(sender, str(sender))
        target_chat_id, _ = self.parse_target_chat(target_chat_str)
        
        file_type = self.media_processor.get_file_type(file_path)
        thumb_path = self.get_thumbnail_path(sender)
        
        progress_args = ("╭──────────────╮\n│ **__4GB Uploader ⚡__**\n├────────", edit_msg, time.time())
        
        sent_to_log = False
        try:
            if file_type == 'video':
                metadata = {}
                if 'video_metadata' in globals():
                    metadata = video_metadata(file_path)
                
                result = await self.pro_client.send_video(
                    LOG_GROUP,
                    video=file_path,
                    caption=caption,
                    thumb=thumb_path,
                    height=metadata.get('height', 0),
                    width=metadata.get('width', 0),
                    duration=metadata.get('duration', 0),
                    progress=progress_bar,
                    progress_args=progress_args
                )
            else:
                result = await self.pro_client.send_document(
                    LOG_GROUP,
                    document=file_path,
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_bar,
                    progress_args=progress_args
                )
            sent_to_log = True

            # Check if user is premium or free
            free_check = 0
            if 'chk_user' in globals():
                free_check = await chk_user(sender, sender)

            if free_check == 1:
                # Free user - send with protection
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton("💎 Get Premium to Forward", url="https://t.me/kingofpatal")
                ]])
                await app.copy_message(target_chat_id, LOG_GROUP, result.id, protect_content=True, reply_markup=reply_markup)
            else:
                # Premium user - send normally
                await app.copy_message(target_chat_id, LOG_GROUP, result.id)

        except Exception as e:
            print(f"Large file upload error: {e}")
            await safe_log(f"**4GB Upload Error:** {str(e)}")
            if not sent_to_log:
                # LOG_GROUP unreachable — upload straight to the user's target instead
                try:
                    if file_type == 'video':
                        await self.pro_client.send_video(
                            target_chat_id,
                            video=file_path,
                            caption=caption,
                            thumb=thumb_path,
                            progress=progress_bar,
                            progress_args=progress_args
                        )
                    else:
                        await self.pro_client.send_document(
                            target_chat_id,
                            document=file_path,
                            caption=caption,
                            thumb=thumb_path,
                            progress=progress_bar,
                            progress_args=progress_args
                        )
                except Exception as e2:
                    await safe_log(f"**4GB direct upload also failed:** {str(e2)}")
        finally:
            await edit_msg.delete()

    async def handle_message_download(self, userbot, sender: int, edit_id: int, msg_link: str, offset: int, message):
        """Main message processing function with enhanced error handling"""
        edit_msg = None
        file_path = None
        
        try:
            # Parse and validate message link
            msg_link = msg_link.split("?single")[0]
            protected_channels = self.db.get_protected_channels()
            
            # Extract chat and message info
            chat_id, msg_id = await self._parse_message_link(msg_link, offset, protected_channels, sender, edit_id)
            if not chat_id:
                return
            
            # Get target chat configuration
            # First check in-memory cache, then fall back to MongoDB
            target_chat_str = self.user_chat_ids.get(message.chat.id)
            if not target_chat_str:
                try:
                    saved_data = await odb.get_data(message.chat.id)
                    if saved_data and saved_data.get("chat_id"):
                        target_chat_str = str(saved_data["chat_id"])
                        self.user_chat_ids[message.chat.id] = target_chat_str  # cache it
                except Exception:
                    pass
            if not target_chat_str:
                target_chat_str = str(message.chat.id)
            target_chat_id, topic_id = self.parse_target_chat(target_chat_str)
            
            # Fetch message
            msg = await userbot.get_messages(chat_id, msg_id)
            if not msg or msg.service or msg.empty:
                await app.delete_messages(sender, edit_id)
                return
            
            # Handle special message types
            if await self._handle_special_messages(msg, target_chat_id, topic_id, edit_id, sender):
                return
                
            # Process media files
            if not msg.media:
                return
            
            filename, file_size, media_type = self.media_processor.get_media_info(msg)
            
            # Handle direct media types (voice, video_note, sticker)
            if await self._handle_direct_media(msg, target_chat_id, topic_id, edit_id, media_type):
                return
            
            # Download file
            edit_msg = await app.edit_message_text(sender, edit_id, "**📥 Downloading...**")
            
            progress_args = ("╭──────────────╮\n│ **__Downloading...__**\n├────────", edit_msg, time.time())
            file_path = await userbot.download_media(
                msg, file_name=filename, progress=progress_bar, progress_args=progress_args
            )
            
            # Process caption and filename
            caption = await self.process_user_caption(msg.caption.markdown if msg.caption else "", sender)
            file_path = await self.file_ops.process_filename(file_path, sender)
            
            # Handle photos separately
            if media_type == "photo":
                result = await app.send_photo(target_chat_id, file_path, caption=caption, reply_to_message_id=topic_id)
                await log_copy(result)
                await edit_msg.delete()
                return
            
            # Check file size and handle accordingly
            upload_method = self.db.get_user_data(sender, "upload_method", "Pyrogram")
            
            if file_size > self.config.SIZE_LIMIT:
                free_check = 0
                if 'chk_user' in globals():
                    free_check = await chk_user(chat_id, sender)
                
                if free_check == 1 or not self.pro_client:
                    # Split file for free users or when pro client unavailable
                    await edit_msg.delete()
                    await self.file_ops.split_large_file(file_path, app, sender, target_chat_id, caption, topic_id)
                    return
                else:
                    # Use 4GB uploader
                    await self.handle_large_file_upload(file_path, sender, edit_msg, caption)
                    return
            
            # Regular upload
            if upload_method == "Telethon" and gf:
                await self.upload_with_telethon(file_path, sender, target_chat_id, caption, topic_id, edit_msg)
            else:
                await self.upload_with_pyrogram(file_path, sender, target_chat_id, caption, topic_id, edit_msg)
                    
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid) as e:
            await app.edit_message_text(sender, edit_id, "❌ Access denied. Have you joined the channel?")
        except Exception as e:
            print(f"Error in message handling: {e}")
            await safe_log(f"**Error:** {str(e)}")
        finally:
            # Cleanup
            if file_path:
                await self.file_ops._cleanup_file(file_path)
            gc.collect()

    async def _parse_message_link(self, msg_link: str, offset: int, protected_channels: Set[int], sender: int, edit_id: int) -> Tuple[Optional[int], Optional[int]]:
        """Parse different types of message links"""
        if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
            parts = msg_link.split("/")
            if 't.me/b/' in msg_link:
                chat_id = parts[-2]
                msg_id = int(parts[-1]) + offset
            else:
                chat_id = int('-100' + parts[parts.index('c') + 1])
                msg_id = int(parts[-1]) + offset
            
            if chat_id in protected_channels:
                await app.edit_message_text(sender, edit_id, "❌ This channel is protected by **Maderauchiha**.")
                return None, None
                
            return chat_id, msg_id
        
        elif '/s/' in msg_link:
            # Handle story links
            await app.edit_message_text(sender, edit_id, "📖 Story Link Detected...")
            if not gf:
                await app.edit_message_text(sender, edit_id, "❌ Login required to save stories...")
                return None, None
            
            parts = msg_link.split("/")
            chat = f"-100{parts[3]}" if parts[3].isdigit() else parts[3]
            msg_id = int(parts[-1])
            await self._download_user_stories(gf, chat, msg_id, sender, edit_id)
            return None, None
        
        else:
            # Handle public links
            await app.edit_message_text(sender, edit_id, "🔗 Public link detected...")
            chat = msg_link.split("t.me/")[1].split("/")[0]
            msg_id = int(msg_link.split("/")[-1])
            await self._copy_public_message(app, gf, sender, chat, msg_id, edit_id)
            return None, None

    async def _handle_special_messages(self, msg, target_chat_id: int, topic_id: Optional[int], edit_id: int, sender: int) -> bool:
        """Handle special message types that don't require downloading"""
        if msg.media == MessageMediaType.WEB_PAGE_PREVIEW:
            result = await app.send_message(target_chat_id, msg.text.markdown, reply_to_message_id=topic_id)
            await log_copy(result)
            await app.delete_messages(sender, edit_id)
            return True
        
        if msg.text:
            result = await app.send_message(target_chat_id, msg.text.markdown, reply_to_message_id=topic_id)
            await log_copy(result)
            await app.delete_messages(sender, edit_id)
            return True
            
        return False

    async def _handle_direct_media(self, msg, target_chat_id: int, topic_id: Optional[int], edit_id: int, media_type: str) -> bool:
        """Handle media that can be sent directly without downloading"""
        result = None
        
        try:
            if media_type == "sticker":
                result = await app.send_sticker(target_chat_id, msg.sticker.file_id, reply_to_message_id=topic_id)
            elif media_type == "voice":
                result = await app.send_voice(target_chat_id, msg.voice.file_id, reply_to_message_id=topic_id)
            elif media_type == "video_note":
                result = await app.send_video_note(target_chat_id, msg.video_note.file_id, reply_to_message_id=topic_id)
            
            if result:
                await log_copy(result)
                await app.delete_messages(msg.chat.id, edit_id)
                return True
                
        except Exception as e:
            print(f"Direct media send failed: {e}")
            return False
            
        return False

    async def _download_user_stories(self, userbot, chat_id: str, msg_id: int, sender: int, edit_id: int):
        """Download and send user stories"""
        try:
            edit_msg = await app.edit_message_text(sender, edit_id, "📖 Downloading Story...")
            story = await userbot.get_stories(chat_id, msg_id)
            
            if not story or not story.media:
                await edit_msg.edit("❌ No story available or no media.")
                return
            
            file_path = await userbot.download_media(story)
            await edit_msg.edit("📤 Uploading Story...")
            
            if story.media == MessageMediaType.VIDEO:
                await app.send_video(sender, file_path)
            elif story.media == MessageMediaType.DOCUMENT:
                await app.send_document(sender, file_path)
            elif story.media == MessageMediaType.PHOTO:
                await app.send_photo(sender, file_path)
            
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            await edit_msg.edit("✅ Story processed successfully.")
            
        except RPCError as e:
            await app.edit_message_text(sender, edit_id, f"❌ Error: {e}")

    async def _copy_public_message(self, app_client, userbot, sender: int, chat_id: str, message_id: int, edit_id: int):
        """Handle copying from public channels/groups"""
        # Check in-memory cache first, then fall back to MongoDB (same pattern as handle_message_download)
        target_chat_str = self.user_chat_ids.get(sender)
        if not target_chat_str:
            try:
                saved_data = await odb.get_data(sender)
                if saved_data and saved_data.get("chat_id"):
                    target_chat_str = str(saved_data["chat_id"])
                    self.user_chat_ids[sender] = target_chat_str  # cache it
            except Exception:
                pass
        if not target_chat_str:
            target_chat_str = str(sender)
        target_chat_id, topic_id = self.parse_target_chat(target_chat_str)
        file_path = None
        
        try:
            # Try direct copy first
            msg = await app_client.get_messages(chat_id, message_id)
            custom_caption = self.user_caption_prefs.get(str(sender), "")
            final_caption = await self._format_caption_with_custom(msg.caption or '', sender, custom_caption)

            # Try direct copy for ALL media/text types first (works on non-forward-restricted channels)
            if msg.media or msg.text:
                try:
                    result = await app_client.copy_message(
                        target_chat_id, chat_id, message_id, reply_to_message_id=topic_id
                    )
                    await log_copy(result)
                    await app.delete_messages(sender, edit_id)
                    return
                except Exception:
                    pass  # Forward-restricted or inaccessible — fall through to userbot path

            # Direct copy failed; try with userbot
            if not userbot:
                # No userbot available — tell the user instead of silently doing nothing
                try:
                    await app.edit_message_text(
                        sender, edit_id,
                        "❌ **Cannot extract this content.**\n\n"
                        "This channel has forward protection enabled.\n"
                        "Use /login to connect your Telegram account and try again."
                    )
                except Exception:
                    pass
                return

            if userbot:
                edit_msg = await app.edit_message_text(sender, edit_id, "🔄 Trying alternative method...")
                try:
                    await userbot.join_chat(chat_id)
                except:
                    pass
                
                chat_id = (await userbot.get_chat(f"@{chat_id}")).id
                msg = await userbot.get_messages(chat_id, message_id)

                if not msg or msg.service or msg.empty:
                    await edit_msg.edit("❌ Message not found or inaccessible")
                    return

                if msg.text:
                    await app_client.send_message(target_chat_id, msg.text.markdown, reply_to_message_id=topic_id)
                    await edit_msg.delete()
                    return

                # Download and upload media
                final_caption = await self._format_caption_with_custom(msg.caption.markdown if msg.caption else "", sender, custom_caption)
                
                progress_args = ("Downloading...", edit_msg, time.time())
                file_path = await userbot.download_media(msg, progress=progress_bar, progress_args=progress_args)
                file_path = await self.file_ops.process_filename(file_path, sender)

                filename, file_size, media_type = self.media_processor.get_media_info(msg)

                if media_type == "photo":
                    result = await app_client.send_photo(target_chat_id, file_path, caption=final_caption, reply_to_message_id=topic_id)
                elif file_size > self.config.SIZE_LIMIT:
                    free_check = 0
                    if 'chk_user' in globals():
                        free_check = await chk_user(chat_id, sender)
                    
                    if free_check == 1 or not self.pro_client:
                        await edit_msg.delete()
                        await self.file_ops.split_large_file(file_path, app_client, sender, target_chat_id, final_caption, topic_id)
                        return
                    else:
                        await self.handle_large_file_upload(file_path, sender, edit_msg, final_caption)
                        return
                else:
                    upload_method = self.db.get_user_data(sender, "upload_method", "Pyrogram")
                    if upload_method == "Telethon":
                        await self.upload_with_telethon(file_path, sender, target_chat_id, final_caption, topic_id, edit_msg)
                    else:
                        await self.upload_with_pyrogram(file_path, sender, target_chat_id, final_caption, topic_id, edit_msg)

        except Exception as e:
            print(f"Public message copy error: {e}")
            # Notify the user — previously errors were swallowed silently
            try:
                await app.edit_message_text(
                    sender, edit_id,
                    f"❌ **Upload failed.**\n\n"
                    f"Could not send to your configured channel.\n"
                    f"Make sure the **bot is an admin** in the channel with post permission.\n\n"
                    f"Error: `{type(e).__name__}: {str(e)[:200]}`\n\n"
                    f"Use `/removechannel` to revert to DM, or re-add the bot as admin and try again."
                )
            except Exception:
                pass
        finally:
            if file_path:
                await self.file_ops._cleanup_file(file_path)

    async def _format_caption_with_custom(self, original_caption: str, sender: int, custom_caption: str) -> str:
        """Format caption with user preferences"""
        delete_words = set(self.db.get_user_data(sender, "delete_words", []))
        replacements = self.db.get_user_data(sender, "replacement_words", {})
        
        processed = original_caption
        for word in delete_words:
            processed = processed.replace(word, '  ')
        
        for word, replace_word in replacements.items():
            processed = processed.replace(word, replace_word)
        
        if custom_caption:
            return f"{processed}\n\n__**{custom_caption}**__" if processed else f"__**{custom_caption}**__"
        return processed


# Initialize the main bot instance
telegram_bot = SmartTelegramBot()

# Main message handler function (integration point with existing get_msg function)
async def get_msg(userbot, sender, edit_id, msg_link, i, message):
    """Main integration function - enhanced version of original get_msg"""
    await telegram_bot.handle_message_download(userbot, sender, edit_id, msg_link, i, message)

print("✅ Smart Telegram Bot initialized successfully!")
print(f"📊 Features loaded:")
print(f"   • Database: {'✅' if telegram_bot.db else '❌'}")
print(f"   • Pro Client (4GB): {'✅' if telegram_bot.pro_client else '❌'}")
print(f"   • Userbot: {'✅' if gf else '❌'}")
print(f"   • App Client: {'✅' if app else '❌'}")
