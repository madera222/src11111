# ⚡ Quick Start Guide - 5 Minutes Setup

## Step 1️⃣: Get API Credentials (2 min)

### API_ID અને API_HASH લેવા

1. https://my.telegram.org/auth પર જાઓ
2. તમારા phone number સાથે login કરો
3. "API development tools" પર ક્લિક કરો
4. **API_ID** કોપી કરો
5. **API_HASH** કોપી કરો

### BOT_TOKEN લેવો

1. Telegram માં [@BotFather](https://t.me/botfather) સર્ચ કરો
2. `/start` ટાઈપ કરો
3. `/newbot` ટાઈપ કરો
4. Bot નાનું નામ આપો (e.g., "MyContentBot")
5. Unique username આપો (e.g., "my_content_bot_123")
6. **token** કોપી કરો

### OWNER_ID લેવો

1. Telegram માં [@userinfobot](https://t.me/userinfobot) સર્ચ કરો
2. `start` ટાઈપ કરો
3. તમારો **ID** નીચે આવશે
4. ID કોપી કરો

---

## Step 2️⃣: Setup MongoDB (2 min)

### FREE Database બનાવો

1. https://mongodb.com/cloud/atlas પર જાઓ
2. Free account બનાવો
3. **Cluster** બનાવો (Free tier select કરો)
4. Username અને Password સેટ કરો
5. "Connect" પર ક્લિક કરો
6. Connection string કોપી કરો

Example:
```
mongodb+srv://username:password@cluster0.mongodb.net/?appName=Cluster0
```

---

## Step 3️⃣: Config Update (1 min)

### `config.py` File ખોલો અને ભરો

```python
# ✅ આ values આપી છો તે અહીં મૂકો

API_ID       = "12345678"                    # my.telegram.org થી
API_HASH     = "abcd1234efgh5678ijkl"       # my.telegram.org થી
BOT_TOKEN    = "123456:ABCDefghIJKlmn"      # @BotFather થી
OWNER_ID     = [1234567890]                 # @userinfobot થી
MONGO_DB     = "mongodb+srv://user:pass@..." # MongoDB Connection String
```

---

## Step 4️⃣: Install & Run (Depends on System)

### **Windows:**

```bash
# Open Command Prompt and run:
pip install -r requirements.txt
python -m devgagan
```

### **Linux/Mac:**

```bash
# Open Terminal and run:
pip3 install -r requirements.txt
python3 -m devgagan
```

### **VPS (screen background running):**

```bash
# Background run કરવા માટે:
screen -S telegram_bot
python3 -m devgagan

# Detach: Ctrl+A, then Ctrl+D
# Reattach: screen -r telegram_bot
```

---

## Step 5️⃣: Test Bot

### Telegram માં Bot સર્ચ કરો અને test કરો:

```
/start → ✅ Bot reply આવે
/login → ✅ Phone number પોચ્છે
/help → ✅ Help આવે
```

---

## 🔴 Common Problems & Quick Fixes

### ❌ "Invalid API ID/Hash"
```
✅ Fix:
- https://my.telegram.org/auth પર જાઓ
- API_ID અને API_HASH ફરી કોપી કરો
- Exactly copy કરો (કોઈ space નહીં)
```

### ❌ "ModuleNotFoundError"
```
✅ Fix:
pip install -r requirements.txt
```

### ❌ "MongoDB Connection Error"
```
✅ Fix:
- MongoDB URL ચેક કરો
- Username અને password સાધારણ છે?
- Network access enable કર્યો છે?
```

### ❌ "OTP Not Receiving"
```
✅ Fix:
- Phone format સાધારણ: +919876543210
- 2-3 મિનિટ રાહ જુઓ
- API_ID/HASH ચેક કરો
```

---

## 📝 Example - Full Config

```python
# ✅ આ રીતે દેખાવું જોઈએ

API_ID       = "9876543"
API_HASH     = "a1b2c3d4e5f6g7h8i9j0"
BOT_TOKEN    = "1234567890:ABCDEfghijklmnopqrst"
OWNER_ID     = [1234567890]
MONGO_DB     = "mongodb+srv://admin123:pass@cluster0.r2pwqnt.mongodb.net/?appName=Cluster0"
```

---

## ✅ Success Checklist

- [ ] API Credentials મેળવ્યા
- [ ] MongoDB URL તૈયાર છે
- [ ] config.py update કર્યું
- [ ] requirements.txt install કર્યું
- [ ] Bot start થઈ ગયો
- [ ] `/start` command કામ કરે છે
- [ ] Bot online છે Telegram માં

---

## 🚀 Next Steps

1. **Login કરો:**
   ```
   /login
   ```

2. **Content extract કરો:**
   ```
   તમે જે channel/group માંથી content લેવો તે link share કરો
   ```

3. **Broadcast કરો:**
   ```
   /broadcast
   ```

---

## 📚 More Help

- **Gujarati Guide:** `GUJARATI_GUIDE.md` વાંચો
- **Full Changelog:** `CHANGES.md` વાંચો
- **Original Docs:** `README.md` વાંચો

---

**Time to Setup:** ~5 minutes ⏱️  
**Difficulty:** ⭐ Easy  
**Support:** Self-hosted (personal use)

