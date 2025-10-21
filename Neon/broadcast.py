from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from database.db import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time
from pyrogram.types import Message
import json
import os

# ─────────────────────────────
# Broadcast helper function
# ─────────────────────────────
async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception:
        return False, "Error"

# ─────────────────────────────
# /broadcast command
# ─────────────────────────────
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def verupikkals(bot, message):
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "**__Reply This Command To Your Broadcast Message__**",
            quote=True
        )

    users = await db.get_all_users()
    sts = await message.reply_text(
        text='**__Broadcasting Your Messages...__**',
        quote=True
    )

    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg)
            if pti:
                success += 1
            elif pti == False:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            done += 1

            if not done % 20:
                await sts.edit(
                    f"**__Broadcast In Progress:__**\n\n"
                    f"**👥 __Total Users:** {total_users}__\n"
                    f"**💫 __Completed:** {done} / {total_users}__\n"
                    f"**✅ __Success :** {success}__\n"
                    f"**🚫 __Blocked :** {blocked}__\n"
                    f"**🚮 __Deleted :** {deleted}__"
                )
        else:
            done += 1
            failed += 1
            if not done % 20:
                await sts.edit(
                    f"**__Broadcast In Progress:__**\n\n"
                    f"**👥 __Total Users:** {total_users}__\n"
                    f"**💫 __Completed:** {done} / {total_users}__\n"
                    f"**✅ __Success :** {success}__\n"
                    f"**🚫 __Blocked :** {blocked}__\n"
                    f"**🚮 __Deleted :** {deleted}__"
                )

    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(
        f"**__Broadcast Completed:__**\n"
        f"**⏰ __Completed in:** {time_taken}__\n\n"
        f"**👥 __Total Users:** {total_users}__\n"
        f"**💫 __Completed:** {done} / {total_users}__\n"
        f"**✅ __Success :** {success}__\n"
        f"**🚫 __Blocked :** {blocked}__\n"
        f"**🚮 __Deleted :** {deleted}__"
    )

# ─────────────────────────────
# /users Command (Standalone + JSON export)
# ─────────────────────────────
@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users_count(bot: Client, message: Message):
    """Shows total registered users for admins and sends a SaveRestricted.json file."""
    msg = await message.reply_text("⏳ <b>Gathering user data...</b>", quote=True)

    try:
        # 1) Count & show
        total = await db.total_users_count()
        await msg.edit_text(
            f"""
🌀 <b><i>User Analytics Update</i></b> 🌀

👥 <b>Total Registered Users:</b> <code>{total}</code>
🛰 <b>System Status:</b> Active ✅
🧠 <b>Data Source:</b> MongoDB (async)
"""
        )

        # 2) Fetch all users and build list
        users_cursor = await db.get_all_users()
        users_list = []
        async for user in users_cursor:
            # Make fields consistent with your requested format
            users_list.append({
                "name": user.get("name", "None"),
                "username": user.get("username", "None"),
                "id": user.get("id")
            })

        # 3) Write to JSON file with fixed name
        tmp_path = "SaveRestricted.json"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(users_list, f, indent=2, ensure_ascii=False)

        # 4) Send the JSON file to the admin who requested it
        caption = f"📄 Recorded {len(users_list)} Users"
        await message.reply_document(
            document=tmp_path,
            caption=caption,
            quote=True
        )

        # 5) Clean up the file after sending
        try:
            os.remove(tmp_path)
        except Exception as e:
            print(f"[!] Failed to delete file {tmp_path}: {e}")

    except Exception as e:
        await msg.edit_text(f"⚠️ Error fetching user data:\n<code>{e}</code>")
        print(f"[!] /users error: {e}")


# Dont remove Credits
# Developer Telegram @MyselfNeon
# Update channel - @NeonFiles
