from pyrogram import Client, filters
from pymongo import MongoClient
import json
import os
from datetime import datetime
import pytz
from config import DB_URI, DB_NAME

# Neon-style MongoDB setup 🚀
neon = MongoClient(DB_URI)
db = neon[DB_NAME]
users_collection = db["users"]

# Timezone for IST
IST = pytz.timezone("Asia/Kolkata")

@Client.on_message(filters.command("users") & filters.user([your_user_id_here]))  # replace with your Telegram ID
async def list_users(client, message):
    try:
        users = list(users_collection.find({}, {"_id": 0}))
        total_users = len(users)

        if total_users == 0:
            await message.reply_text("No users found in the database 🥲")
            return

        # 1️⃣ Send the total users count as a separate message
        await message.reply_text(f"👥 Total Registered Users: {total_users}")

        # 2️⃣ Create JSON file
        json_data = json.dumps(users, indent=4, ensure_ascii=False)
        file_path = "SaveRestricted Users.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        # Get current IST date and time (short month name)
        current_time = datetime.now(IST).strftime("%d %b %Y | %I:%M %p")

        # 3️⃣ Send JSON file with timestamp as caption
        await message.reply_document(file_path, caption=current_time)

        # Cleanup the file
        os.remove(file_path)

    except Exception as e:
        await message.reply_text(f"⚠️ Error while fetching users:\n`{e}`")
