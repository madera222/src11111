# 🤖 Personal Telegram Content Extractor Bot - ગુજરાતી ગાઈડ

આ bot તમારી પોતાની personal Telegram account માટે બનાવવામાં આવ્યો છે.

---

## 📋 બોટ શું કરે છે?

✅ Telegram channels/groups માંથી content download કરે છે  
✅ Video, photo, audio સب કાંઈ extract કરી શકે છે  
✅ તમારા personal account સાથે login કરીને কাজ કરે છે  
✅ Admin ને broadcast feature આપે છે  

---

## 🔧 Setup કરવાનું (આ જરૂર છે!)

### Step 1: Config.py ખોલો અને આ values ભરો

```python
API_ID = "તમારો API_ID"           # my.telegram.org થી મેળવો
API_HASH = "તમારો API_HASH"       # my.telegram.org થી મેળવો
BOT_TOKEN = "તમારો BOT_TOKEN"     # @BotFather થી મેળવો
OWNER_ID = [1234567890]            # તમારો User ID (હમેશા list માં)
```

### Step 2: MongoDB Database ચાલુ કરો

```python
MONGO_DB = "mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0"
```

---

## 🔑 Login કમાન્ડ - OTP માટે

### **Steps:**

1. Bot ને `/login` ટાઈપ કરો
2. તમારો phone number આપો (country code સાથે)
   - Example: `+919876543210`
3. Telegram પર OTP આવશે
4. OTP આપો (spaces સાથે)
   - Example: `1 2 3 4 5`
5. જો 2FA ચાલુ છે તો password આપો

### **આ code શું કરે છે?**

```
User → Phone Number → OTP Request → Telegram API
                          ↓
                    તમારા Telegram પર OTP આવે
                          ↓
User → OTP આપે → Sign In → Session String Save થાય
```

---

## 📢 Broadcast Command - બધા Users ને Message મોકલો

### **Command:**
```
/broadcast
```

### **કેવી રીતે વાપરો:**

1. તમે broadcast કરવા માંગો તે message **reply** કરો
2. `/broadcast` ટાઈપ કરો
3. Bot બધા users ને message મોકલશે

### **Example:**
```
User: "Hello everyone! 👋" (reply કરો)
Admin: /broadcast
Bot: તમામ 50 users ને message મોકલશે
```

---

## 📥 Content Extract કરવું

### **Public Channels:**
```
Bot ને link આપો → Content download થાય
```

### **Private/Restricted Channels:**
```
પહેલા `/login` કરો → પછી link આપો → Content download થાય
```

---

## 🔄 Bot Alive Message Fix

### **શું ફિક્સ કર્યું:**
❌ પહેલા: Bot start થતાં બધા OWNER_ID ને અલગ message જતા હતા  
✅ હવે: બસ એક જ વાર message જાય છે (બધું બગડતું નથી)

---

## 🆘 Common Issues & Solutions

### **Problem 1: OTP નથી આવતો**
```
✅ Solution:
- API_ID અને API_HASH ચેક કરો (my.telegram.org પર જાઓ)
- Phone number format સાધારણ હોવો જોઈએ: +919876543210
- 2-3 મિનિટ રાહ જુઓ (Telegram slow હોય તો)
```

### **Problem 2: "Invalid API ID/Hash" Error**
```
✅ Solution:
1. https://my.telegram.org/auth પર જાઓ
2. Log in કરો તમારા account સાથે
3. "API development tools" સમજો
4. API_ID અને API_HASH કોપી કરો
5. Config.py માં પેસ્ટ કરો
```

### **Problem 3: Login success પણ content extract નથી થતું**
```
✅ Solution:
- Channel/Group માટે bot ને permission આપો
- Restricted content માટે પહેલા `/login` કરો જરૂર છે
```

### **Problem 4: MongoDB Error**
```
✅ Solution:
- Correct MongoDB URL ચેક કરો
- Database create કર્યો છે?
- Username અને password ચેક કરો
```

---

## 📊 Commands List - બધા Commands

| Command | શું કામ કરે છે | Example |
|---------|-------------|---------|
| `/start` | Bot شروع કરો | `/start` |
| `/login` | Account login કરો | `/login` |
| `/logout` | Account logout કરો | `/logout` |
| `/broadcast` | બધા users ને message મોકલો | `/broadcast` |
| `/settings` | Settings બદલો | `/settings` |
| `/myplan` | તમારી plan જુઓ | `/myplan` |
| `/help` | Help આપશે | `/help` |

---

## 🎯 Workflow - બોટ કેવી રીતે કામ કરે છે

```
┌─────────────────────────────────────┐
│  Bot Start થાય                     │
│  ✅ Startup message (1 વાર જ)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User /login આપે                  │
│  - Phone number લે                  │
│  - OTP મોકલે                       │
│  - Session string save કરે          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Link આપે user                    │
│  - Content extract થાય             │
│  - Download થાય                    │
│  - Telegram પર upload થાય          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  /broadcast વાપરો                 │
│  - બધા users ને message જાય       │
└─────────────────────────────────────┘
```

---

## 🔐 Privacy & Security

⚠️ **Important:**
- API_ID, API_HASH, BOT_TOKEN **कभी public ન કરશો**
- Session string **private રાખો**
- Config.py **.gitignore માં ઉમેરો** (GitHub પર push ન કરો)

---

## 🛠️ Troubleshooting

### Bot start થવા માટે requirements:

```bash
pip install -r requirements.txt
```

### Bot start કરવાનું:

```bash
# Terminal/Command Prompt માં:
python -m devgagan

# અથવા:
python devgagan/__main__.py
```

### Logs જુઓ:

```bash
# Screen માટે (Linux/Mac):
screen -S bot
python -m devgagan

# Detach કરવા માટે:
Ctrl + A, પછી Ctrl + D

# Reattach કરવા માટે:
screen -r bot
```

---

## 📝 Changes Summary - આ Release માં શું બદલાયું

### ✅ Fixed:
1. **Bot Alive Message** - હવે બસ 1 વાર જાય છે (duplicate messages ફિક્સ)
2. **Login/OTP Flow** - Better error handling, Gujarati messages, proper client disconnect
3. **Broadcast Command** - Import errors fixed, better status reporting
4. **Error Handling** - બધા جگહોએ try-catch properly લાગાવ્યા

### 📢 Added:
1. **Gujarati Documentation** - આ ફાઈલ જ!
2. **Better Error Messages** - Gujarati માં સમજાય તેવા errors
3. **Improved Broadcast** - Progress tracking અને detailed report

---

## 💡 Pro Tips

1. **Session String Save કરો**: Login પછી session string backup કરો
2. **Multiple Channels**: `/setchannel` વાપરીને upload destination બદલો
3. **Batch Processing**: એક સાથે ધણાં links process કરો
4. **Scheduled Broadcasts**: Cron job વાપરીને automatic broadcasts કરો

---

## 📞 Support

```
❌ Problem હોય તો:
- Logs જુઓ (જવાબ મોટે ભાગે logs માં હોય છે)
- Error message ધ્યાનથી વાંચો
- Config.py ફરી ચેક કરો
- Database connection verify કરો
```

---

**Made with ❤️ for Personal Use**  
**Version: 2.0.6 (Fixed & Enhanced)**  
**Last Updated: 2025-01-15**

