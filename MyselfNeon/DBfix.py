# ---------------------------------------------------
# File Name: FixDB.py
# Description: Fixes missing usernames in MongoDB
# Author: NeonAnurag (Modified by Assistant)
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from database.db import db
from config import ADMINS
import asyncio
import time

@Client.on_message(filters.command("fix_usernames") & filters.user(ADMINS))
async def fix_usernames_command(bot: Client, message: Message):
    # 1. Notify Admin
    sts = await message.reply_text(
        "⏳ **Scanning database to fix missing usernames...**\n"
        "<i>This may take a while depending on user count.</i>"
    )

    # 2. Get all users
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    
    # 3. Counters
    fixed = 0
    skipped = 0
    deleted = 0
    failed = 0
    
    start_time = time.time()

    async for user in users:
        user_id = user.get('id')
        current_username = user.get('username')

        # If username is already present, skip
        if current_username:
            skipped += 1
            continue

        # If username is missing, fetch from Telegram
        try:
            # We add a small delay to avoid hitting limits too fast
            await asyncio.sleep(0.5) 
            
            chat = await bot.get_chat(user_id)
            
            # If the user has a username, update it in DB
            if chat.username:
                await db.update_username(user_id, chat.username)
                fixed += 1
            else:
                # User has no username set on Telegram, set as "None" explicitly
                await db.update_username(user_id, "None")
                skipped += 1

        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
            # Retry logic could be added here, but for simplicity we skip to next to keep moving
            failed += 1
            
        except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
            # User deleted account or blocked bot
            # Optional: You can uncomment the next line to delete dead users
            # await db.delete_user(user_id)
            deleted += 1
            
        except Exception as e:
            print(f"[FixDB] Error for {user_id}: {e}")
            failed += 1

        # 4. Update Status every 20 processed users
        if (fixed + skipped + deleted + failed) % 20 == 0:
            await sts.edit(
                f"**🛠 Database Repair In Progress**\n\n"
                f"👥 **Total Scanned:** {fixed + skipped + deleted + failed} / {total_users}\n"
                f"✅ **Fixed:** {fixed}\n"
                f"⏭ **Skipped (Already had username):** {skipped}\n"
                f"🚫 **Deleted/Blocked:** {deleted}\n"
                f"⚠️ **Errors:** {failed}"
            )

    # 5. Final Report
    time_taken = int(time.time() - start_time)
    await sts.edit(
        f"**✅ Database Repair Completed!**\n\n"
        f"⏱ **Time Taken:** {time_taken}s\n"
        f"👥 **Total Users:** {total_users}\n"
        f"✅ **Usernames Added:** {fixed}\n"
        f"🚫 **Dead Accounts:** {deleted}"
    )
