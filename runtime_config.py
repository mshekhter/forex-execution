# =========================
# RUNTIME CONFIG
# =========================

API_BASE_URL = "https://ciapi.cityindex.com/tradingapi"
BASE_V2      = "https://ciapi.cityindex.com/v2"


# Email
USE_EMAIL = False
EMAIL_SENDER   = require_secret("EMAIL_SENDER")   if USE_EMAIL else None
EMAIL_RECEIVER = require_secret("EMAIL_RECEIVER") if USE_EMAIL else None
EMAIL_PASSWORD = require_secret("EMAIL_PASSWORD") if USE_EMAIL else None

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587

# Telegram
USE_TELEGRAM = True
TELEGRAM_BOT_TOKEN = require_secret("TELEGRAM_BOT_TOKEN") if USE_TELEGRAM else None
TELEGRAM_CHAT_ID  = require_secret("TELEGRAM_CHAT_ID")  if USE_TELEGRAM else None

print("Runtime config loaded")
