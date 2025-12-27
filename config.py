# ---------------------------------------------------
# File Name: Config.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# Last Modified: 2025-11-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import os

# Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID & Hash
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", ""))

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "SaveRestricted")

# Log Channel to Track New Users 
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002322660786"))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then False
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

# Keep-Alive URL
KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "https://sastrictions-bot.onrender.com")

# Start pic on /start 
START_PIC = os.environ.get("START_PIC", "https://files.catbox.moe/krxuel.jpg")

# -------------------
# VERIFICATION CONFIG
# -------------------
VERIFY = bool(os.environ.get('VERIFY', True)) # Set True to enable
VERIFY_SHORTLINK_URL = os.environ.get('VERIFY_SHORTLINK_URL', 'linkshortify.com') # Your Shortener Domain
VERIFY_SHORTLINK_API = os.environ.get('VERIFY_SHORTLINK_API', '988bdae35d47313de5038650f31c1d1e2a541e98') # Your Shortener API Key
VERIFY_TUTORIAL = os.environ.get('VERIFY_TUTORIAL', 'https://t.me/open_movie_links/6') # Tutorial Link


# MyselfNeon
# Don't Remove Credit 🥺
# Telegram Channel @NeonFiles
