# ---------------------------------------------------
# File Name: Verify.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# Last Modified: 2025-11-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import logging
import random
import string
import asyncio
import aiohttp
from datetime import datetime, timedelta
from shortzy import Shortzy
from config import VERIFY_SHORTLINK_URL, VERIFY_SHORTLINK_API, VERIFY, LOG_CHANNEL
from database.db import db

async def get_verify_shorted_link(link):
    if VERIFY_SHORTLINK_URL == "api.shareus.io":
        url = f'https://{VERIFY_SHORTLINK_URL}/easy_api'
        params = {"key": VERIFY_SHORTLINK_API, "link": link}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    return await response.text()
        except Exception as e:
            logging.error(f"Shortener Error: {e}")
            return link
    else:
        try:
            shortzy = Shortzy(api_key=VERIFY_SHORTLINK_API, base_site=VERIFY_SHORTLINK_URL)
            return await shortzy.convert(link)
        except Exception as e:
            logging.error(f"Shortzy Error: {e}")
            return link

async def get_token(bot, user_id, start_link):
    # Ensure user exists in DB first
    if not await db.is_user_exist(user_id):
        user = await bot.get_users(user_id)
        await db.add_user(user_id, user.first_name)

    # Generate Token
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    
    # Save token to MongoDB
    await db.update_verify_token(user_id, token)
    
    link = f"{start_link}verify-{user_id}-{token}"
    return await get_verify_shorted_link(link)

async def check_token(user_id, token):
    # Get stored token from MongoDB
    stored_token = await db.get_verify_token(user_id)
    
    # Check if token exists and matches
    if stored_token and stored_token == token:
        return True
    return False

async def verify_user(bot, user_id, token):
    # Save current time to MongoDB
    now = datetime.now()
    await db.update_verify_date(user_id, now)
    
    try:
        user = await bot.get_users(user_id)
        bot_info = await bot.get_me()
        
        await bot.send_message(
            LOG_CHANNEL, 
            f"**⌬ #VERIFIED ✅**\n"
            f"**┟ Bot:** __@{bot_info.username}\n"
            f"**┟ User:** __{user.mention}__\n"
            f"**┟ User ID:** `{user.id}`\n"
            f"**┟ Date:** __{now.strftime('%d %B, %Y')}__\n"
            f"**┖ Time:** __{now.strftime('%I:%M %p')}__"
        )
    except Exception as e:
        print(f"Log Error: {e}")

async def check_verification(user_id):
    if not VERIFY: 
        return True
    
    # Get verification date from MongoDB
    verified_time = await db.get_verify_date(user_id)
    
    if verified_time:
        # Check if current time is less than Verification Time + 4 Hours
        if datetime.now() < verified_time + timedelta(hours=4):
            return True
            
    return False

