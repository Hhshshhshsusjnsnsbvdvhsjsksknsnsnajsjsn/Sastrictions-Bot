from pyrogram import Client, filters
from pyrogram.types import Message
from database import db


# ─────────────────────────────
# Silent User Logger (ignores /users)
# ─────────────────────────────
@Client.on_message(filters.private & ~filters.command("users"))
async def log_user(client: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, user_name)
        print(f"[+] New user added: {user_name} ({user_id})")  # Optional log


# ─────────────────────────────
# /users Command
# ─────────────────────────────
@Client.on_message(filters.command("users") & filters.private)
async def users_count(client: Client, message: Message):
    try:
        msg = await message.reply_text("⏳ <b>Gathering user data...</b>", quote=True)

        total = await db.total_users_count()

        await msg.edit_text(
            f"""
🌀 <b><i>User Analytics Update</i></b> 🌀

👥 <b>Total Registered Users:</b> <code>{total}</code>
🛰 <b>System Status:</b> Active ✅
🧠 <b>Data Source:</b> MongoDB (async)
"""
        )

    except Exception as e:
        await message.reply_text(f"⚠️ Error fetching user data:\n<code>{e}</code>")
        print(f"[!] /users error: {e}")
