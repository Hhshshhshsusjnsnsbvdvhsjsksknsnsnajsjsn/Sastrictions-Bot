# ---------------------------------------------------
# File Name: Verification.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# Last Modified: 2025-11-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import VERIFY, VERIFY_TUTORIAL
from MyselfNeon.verify import get_token, check_verification

@Client.on_message(filters.command("verify"))
async def verify_command_handler(bot, message):
    if not VERIFY:
        return await message.reply("**__♻️ Verification is Currently Disabled.__**")

    if await check_verification(message.from_user.id):
        return await message.reply("✅ **__You are Already Verified for 4 Hours! Enjoy.__**")

    msg = await message.reply("**__Please wait, Generating your Verification Link...__**")
    
    bot_info = await bot.get_me()
    start_link = f"https://t.me/{bot_info.username}?start="
    
    try:
        verify_url = await get_token(bot, message.from_user.id, start_link)
        
        buttons = [
            [InlineKeyboardButton("🔗 Click Here To Verify", url=verify_url)],
            [InlineKeyboardButton("❓ How To Verify", url=VERIFY_TUTORIAL)]
        ]
        
        await msg.edit(
            text="<b><i>🔐 Verification Required !</i></b>\n\n"
                 "<i>To continue using this Bot, you must Verify your Account.</i>\n"
                 "<i>The Token is valid for 4 Hours.</i>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await msg.edit(f"Error generating link: {e}")

@Client.on_callback_query(filters.regex("verify_query"))
async def verify_callback(bot, query):
    await query.message.reply("**__Type /verify to Generate your Link !__**")
    await query.answer()
