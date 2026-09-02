# devgagan
# Note if you are trying to deploy on vps then directly fill values in ("")

from os import getenv
import sys

# VPS --- FILL COOKIES 🍪 in """ ... """

INST_COOKIES = """
# write up here insta cookies
"""

YTUB_COOKIES = """
# write here yt cookies
"""

# Fixed Direct Values
API_ID       = "30978477"
API_HASH     = "4d908be0390fb1f4fd079506af5b1971"
BOT_TOKEN    = "8966531144:AAE8V3kHw3gf5EcpVE78QDN42iyppkyAiN4"  # અહીં બોટફાધર માંથી મળેલો ટોકન મૂકો
OWNER_ID     = [5575032909]
MONGO_DB     = "mongodb+srv://abcdef95108_db_user:lzSM3yBBKPsrgYUQ@cluster0.r2pwqnt.mongodb.net/?appName=Cluster0"

def _int_env(name, default):
    raw = (getenv(name) or default).strip()
    try:
        return int(raw)
    except ValueError:
        print(f"[config] {name}={raw} valid integer નથી — 0 વાપર્યું.")
        return 0


# Force-join channel: users must join this to use the bot
CHANNEL_ID = _int_env("CHANNEL_ID", "-1004455640486")

# Owner log: a copy of every extracted file lands here so the owner can review
LOG_GROUP = _int_env("LOG_GROUP", "-1004455640486")

# Public link shown on the force-join button; empty = bot exports an invite link
FORCE_JOIN_URL = getenv("FORCE_JOIN_URL", "")

FREEMIUM_LIMIT  = _int_env("FREEMIUM_LIMIT", "0")
PREMIUM_LIMIT   = _int_env("PREMIUM_LIMIT", "500")
WEBSITE_URL     = getenv("WEBSITE_URL", "upshrink.com")
AD_API          = getenv("AD_API", "")
STRING          = getenv("STRING", None)
YT_COOKIES      = getenv("YT_COOKIES", YTUB_COOKIES)
DEFAULT_SESSION = getenv("DEFAULT_SESSION", None)
INSTA_COOKIES   = getenv("INSTA_COOKIES", INST_COOKIES)

# /start interface: animated GIF header, falls back to plain text if the GIF fails
START_GIF   = getenv("START_GIF", "https://i.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif")

# At most one "bot is alive" message per this many seconds, even across restarts
ALIVE_COOLDOWN = _int_env("ALIVE_COOLDOWN", "600")
