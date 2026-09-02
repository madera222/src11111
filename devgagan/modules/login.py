# ---------------------------------------------------
# File Name: login.py
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

from pyrogram import filters, Client
from devgagan import app
import random
import os
import asyncio
import string
from devgagan.core.mongo import db
from devgagan.core.func import subscribe, chk_user
from config import API_ID as api_id, API_HASH as api_hash
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait
)

def generate_random_name(length=7):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))  # Editted ... 

async def delete_session_files(user_id):
    session_file = f"session_{user_id}.session"
    memory_file = f"session_{user_id}.session-journal"

    session_file_exists = os.path.exists(session_file)
    memory_file_exists = os.path.exists(memory_file)

    if session_file_exists:
        os.remove(session_file)
    
    if memory_file_exists:
        os.remove(memory_file)

    # Delete session from the database
    if session_file_exists or memory_file_exists:
        await db.remove_session(user_id)
        return True  # Files were deleted
    return False  # No files found

@app.on_message(filters.command("logout"))
async def clear_db(client, message):
    user_id = message.chat.id
    files_deleted = await delete_session_files(user_id)
    try:
        await db.remove_session(user_id)
    except Exception:
        pass

    if files_deleted:
        await message.reply("✅ Your session data and files have been cleared from memory and disk.")
    else:
        await message.reply("✅ Logged out with flag -m")
        
    
@app.on_message(filters.command("login"))
async def generate_session(_, message):
    joined = await subscribe(_, message)
    if joined == 1:
        return
        
    user_id = message.chat.id
    client = None
    
    try:
        # Step 1: Ask for phone number
        number_msg = await _.ask(
            user_id, 
            '📱 **Phone Number આપો**\n\n'
            'તમારો mobile number આપો (country code સાથે)\n'
            'Example: +919876543210', 
            filters=filters.text,
            timeout=300
        )   
        phone_number = number_msg.text.strip()
        
        # Validate phone number format
        if not phone_number.startswith('+'):
            await number_msg.reply('❌ Phone number must start with + (plus sign)\nExample: +919876543210')
            return
            
        # Step 2: Create client and send OTP
        await number_msg.reply("📲 **OTP મોકલી રહ્યા છીએ...**")
        
        client = Client(f"session_{user_id}", api_id, api_hash)
        await client.connect()
        
        try:
            code = await client.send_code(phone_number)
        except ApiIdInvalid:
            await number_msg.reply('❌ API ID/Hash Invalid છે. Config.py ચેક કરો.')
            if client:
                await client.disconnect()
            return
        except PhoneNumberInvalid:
            await number_msg.reply('❌ Phone number Invalid છે. સાધારણ ફોર્મેટ વાપરો: +919876543210')
            if client:
                await client.disconnect()
            return
        except Exception as e:
            await number_msg.reply(f'❌ OTP મોકલતા મુશ્કેલી આવી: {str(e)}\n\nફરી પ્રયાસ કરો.')
            if client:
                await client.disconnect()
            return
        
        # Step 3: Ask for OTP
        try:
            otp_msg = await _.ask(
                user_id, 
                "✅ **OTP આવ્યો હશે!**\n\n"
                "તમારા Telegram account માં OTP આવ્યો હશે.\n"
                "OTP આપો (spaces સાથે)\n"
                "Example: `1 2 3 4 5`", 
                filters=filters.text, 
                timeout=600  # 10 minutes
            )
        except TimeoutError:
            await _.send_message(user_id, '⏰ Time limit 10 minutes ખત્મ થઈ ગઈ. ફરી `/login` કરો.')
            if client:
                await client.disconnect()
            return
        
        phone_code = otp_msg.text.replace(" ", "").strip()
        
        # Step 4: Sign in
        try:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except PhoneCodeInvalid:
            await otp_msg.reply('❌ OTP ખોટો છે. ફરી `/login` કરો અને સાધારણ OTP આપો.')
            if client:
                await client.disconnect()
            return
        except PhoneCodeExpired:
            await otp_msg.reply('❌ OTP એક્સપાયર થઈ ગયો. ફરી `/login` કરો.')
            if client:
                await client.disconnect()
            return
        except SessionPasswordNeeded:
            # Step 5: Handle 2FA password
            try:
                pwd_msg = await _.ask(
                    user_id, 
                    '🔐 **2-Step Verification ચાલુ છે**\n\n'
                    'તમારો password આપો:', 
                    filters=filters.text, 
                    timeout=300  # 5 minutes
                )
            except TimeoutError:
                await _.send_message(user_id, '⏰ Password time limit ખત્મ. ફરી `/login` કરો.')
                if client:
                    await client.disconnect()
                return
            
            try:
                password = pwd_msg.text
                await client.check_password(password=password)
            except PasswordHashInvalid:
                await pwd_msg.reply('❌ Password ખોટો છે. ફરી `/login` કરો.')
                if client:
                    await client.disconnect()
                return
            except Exception as e:
                await pwd_msg.reply(f'❌ Password ચેક કરતા error: {str(e)}')
                if client:
                    await client.disconnect()
                return
        except Exception as e:
            await otp_msg.reply(f'❌ Login error: {str(e)}\n\nફરી `/login` કરો.')
            if client:
                await client.disconnect()
            return
        
        # Step 6: Export and save session
        try:
            string_session = await client.export_session_string()
            await db.set_session(user_id, string_session)
            await otp_msg.reply(
                "✅ **Login Successful!**\n\n"
                "તમારો account logged in થઈ ગયો 🎉\n"
                "હવે તમે restricted content extract કરી શકો છો."
            )
        except Exception as e:
            await otp_msg.reply(f'❌ Session save error: {str(e)}')
            if client:
                await client.disconnect()
            return
            
    except Exception as e:
        await message.reply(f'❌ કંઈક error આવ્યો: {str(e)}\n\nફરી પ્રયાસ કરો.')
    finally:
        # Always disconnect the client
        if client:
            try:
                await client.disconnect()
            except:
                pass
