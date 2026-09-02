# 🎬 Video Extraction Complete Guide

આ guide video extraction કેવી રીતે કામ કરે છે તે સમજાવે છે.

---

## 📹 Video Extraction - Step by Step

### Public Channels/Groups

```
1. Channel/Group link આપો → Bot automatically video download કરે
2. ✅ No login required
3. Video તમારે DM માં આવે
```

### Private/Restricted Channels

```
1. પહેલા /login કરો (તમારો personal account)
2. Channel link આપો
3. ✅ Bot તમારા session વાપરીને video access કરે
4. Video تમારે DM માં આવે
```

---

## 🔑 Video Extraction For Restricted Content

### Requirements

✅ Personal Telegram Account (bot નહીં)  
✅ Access to the channel/group  
✅ Bot کو messaging permission

### Process

```
User Account
    ↓
   /login (OTP)
    ↓
Session String Save થાય
    ↓
तમે Restricted Channel link આપો
    ↓
Bot (તમારे session વાપરીને) Content access કરે
    ↓
Download → Upload to Telegram
```

---

## 📤 Video Upload - How It Works

### Normal Upload (Free)
```
Size: Up to 2GB
Speed: Normal
Quality: Video + Audio both
```

### Premium Upload (4GB Support)
```
Size: Up to 4GB
Speed: Fast
Quality: 4K support

HOW TO ENABLE:
1. તમારો premium Pyrogram V2 session string લો
2. config.py માં STRING variable ભરો
3. Bot restart કરો
```

---

## 🎥 Supported Video Sources

### YouTube/Instagram/Twitter Download

#### Setup کરવું:

```python
# config.py માં:
YT_COOKIES = "your_youtube_cookies"
INSTA_COOKIES = "your_instagram_cookies"
```

#### Cookies કેવી રીતે લો:

**Firefox પર:**
1. Channel/Site open કરો
2. Extensions install કરો: "Export Cookies"
3. Cookies copy કરો
4. Netscape format save કરો

**Chrome પર:**
1. DevTools open કરો (F12)
2. Application → Cookies
3. Manually copy કરો અથવા extension વાપરો

#### Commands:

```
/dl → YouTube/Twitter/Facebook videos download કરો
/adl → Audio ફક્ત download કરો
```

---

## 📊 Video Extraction Settings

### Rename Video

```
Settings → Filename customization
Old: video_123_456.mp4
New: MyCustomName.mp4
```

### Delete Words from Filename

```
Settings → Delete Words
Add: "junk", "temp", "unwanted"

Result: Filenames from "junk_video.mp4" → "video.mp4"
```

### Custom Caption

```
Settings → Add Caption
Before upload, કોઈ text add કરી શકો
```

### Thumbnail

```
Settings → Custom Thumbnail
Upload કરો કોઈ thumbnail અને video માટે use કર
```

---

## 🔄 Batch Video Processing

### Multiple Videos At Once

```
/batch → 
```

#### Commands:

**Add Links:**
```
1. /batch
2. તમે links paste કરો (એક એક line પર)
3. Done → Processing start થાય
```

**Example:**
```
https://t.me/channel_name/123
https://t.me/channel_name/124
https://t.me/channel_name/125
```

**Limits:**
```
Free Users: 0 (disabled by default)
Premium: 500 links per batch
```

---

## 🧪 Testing Video Extraction

### Test 1: Public Channel Video

```
1. کوઈ public Telegram channel find કરો
2. Video message share કરો
3. Bot ને link આપો
4. ✅ Video download થાય તે જુઓ
```

### Test 2: YouTube Video

```
1. /dl command વાપરો
2. YouTube URL આપો
3. ✅ Video download થાય તે જુઓ
```

### Test 3: Restricted Channel Video

```
1. /login સાથે account login કરો
2. Private channel link આપો
3. ✅ Access થાય અને video ખેંચાય તે જુઓ
```

---

## 📊 Video Extraction Status

### Logs ચેક કરો

```bash
# Terminal માં જુઓ:
python -m devgagan

# ✅ Success message:
[INFO] Video extracted: video.mp4
[INFO] Uploading to Telegram...
[INFO] Upload complete!
```

### Problems

```
❌ "Access Denied"
→ Channel access ન હોય અથવા bot blocked હોય

❌ "Video Not Found"
→ Message ID ખોટો હોય

❌ "Download Failed"
→ Network issue અથવા Telegram rate limiting
```

---

## 💾 Storage Management

### Upload Location

```
Default: Your DM
Custom: /setchannel -100XXXXXXXXX
```

### Set Upload Channel

```
1. /setchannel
2. Channel ID આપો
3. ✅ Extracted videos ત્યાં જશે
```

### Get Channel ID

```
1. Channel ખોલો
2. @userinfobot ને forward કરો
3. ID નીચે આવશે
4. /setchannel -100XXXXXXXXX
```

---

## 🚀 Advanced Features

### Fast Upload (Telethon Bridge)

```
✅ SpyLib integration
- ફાસ્ટર upload speed
- Better stability
- Large file support
```

### Direct Topic Upload

```
Topic enabled groups માં directly upload કરી શકો
/setchannel -100XXXXXXXXX/TOPIC_ID
```

### Auto-Pin Messages

```
Settings → Auto-pin enabled
Extracted video automatically pin થશે
```

---

## 🔐 Privacy Notes

### ⚠️ Important:

```
✅ Personal use માટે
✅ તમારો account, તમારો content
✅ Server ધ જ extract નથી કરે (client-based)

❌ ન કરવું:
- કોઈ બીજાનો content copyright ভતર
- Paid content freely distribute કરવો
- Original creator નو credit ન આપવો
```

---

## 📈 Performance Tips

### Fast Extraction

```
1. Good internet connection વાપરો
2. Crowd hours ટાળો
3. Large files માટે রात ટાઈમ best
```

### Save Bandwidth

```
1. Video quality reduce કરો
2. Audio-only download વાપરો (/adl)
3. Batch process નો ઉપયોગ કરો
```

---

## 🆘 Troubleshooting

### Video Download Slow

```
✅ Solutions:
- VPN અથવા proxy ચેક કરો
- Download time zone બદલો
- Later retry કરો
```

### Extracted File Corrupt

```
✅ Solutions:
- Internet connection restart કરો
- File re-download કરો
- Different format try કરો
```

### Telegram Upload Failed

```
✅ Solutions:
- File size ચેક કરો (4GB limit)
- Network restart કરો
- Premium session add કરો (4GB માટે)
```

---

## 📊 Example Workflow

### Complete Video Extraction Journey

```
┌─────────────────────────────┐
│ 1. Start Bot                │
│ /start                      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 2. Login to Account         │
│ /login → OTP                │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 3. Set Upload Location      │
│ /setchannel -100123456      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 4. Configure Settings       │
│ /settings → Customize       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 5. Send Video Link          │
│ https://t.me/channel/123    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 6. Bot Extracts & Uploads   │
│ Processing... ⏳             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 7. Video in Your Channel    │
│ ✅ Complete!                │
└─────────────────────────────┘
```

---

## 📚 More Resources

- **Main Guide:** `GUJARATI_GUIDE.md`
- **Setup:** `SETUP_QUICKSTART.md`
- **All Changes:** `CHANGES.md`

---

**Last Updated:** 2025-01-15  
**Status:** ✅ Fully Functional  
**Tested:** ✅ Yes  

