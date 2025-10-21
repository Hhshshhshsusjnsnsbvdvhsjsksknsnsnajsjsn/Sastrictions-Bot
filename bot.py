# Bot.py
import asyncio
import logging
import datetime
from datetime import timezone, timedelta
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, KEEP_ALIVE_URL, DB_NAME, DB_URI
from pymongo import MongoClient

# ✅ Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))

# Connect to MongoDB using your config
mongo_client = MongoClient(DB_URI)
db = mongo_client[DB_NAME]  # Database; collection auto-created as logged_users

async def keep_alive():
    """Send a request every 300 seconds to keep the bot alive (if required)."""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(KEEP_ALIVE_URL)
                logging.info("Sent keep-alive request.")
            except Exception as e:
                logging.error(f"Keep-alive request failed: {e}")
            await asyncio.sleep(300)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Neon Login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="Neon"),
            workers=50,
            sleep_threshold=10
        )
        self.keep_alive_task = None  # ✅ Track keep-alive task

    async def start(self):  
        await super().start()  
        me = await self.get_me()  

        # Start keep-alive task in background  
        self.keep_alive_task = asyncio.create_task(keep_alive())  

        # Bot Deploy/Restart log  
        now = datetime.datetime.now(IST)  
        text = (  
            f"**🤖 __Bot Deployed / Restarted__ ♻️**\n"  
            f"**- __@{me.username}__**\n\n"  
            f"**- __Date:__** __{now.strftime('%d-%b-%Y')}__\n"  
            f"**- __Time:__** __{now.strftime('%I:%M %p')}__\n"  
            f"**- __@neonfiles __**"  
        )  
        try:  
            await self.send_message(LOG_CHANNEL, text)  
        except Exception as e:  
            print(f"Log send failed: {e}")  

        print(f"**__Bot Powered By @{me.username}__**")  

    async def stop(self, *args):  
        me = await self.get_me()  

        # Stop keep-alive loop if running  
        if self.keep_alive_task:  
            self.keep_alive_task.cancel()  
            try:  
                await self.keep_alive_task  
            except asyncio.CancelledError:  
                pass  

        try:  
            await self.send_message(LOG_CHANNEL, f"❌ Bot @{me.username} Stopped")  
        except Exception as e:  
            print(f"Stop log failed: {e}")  

        await super().stop()  
        print("Bot Stopped Bye")

BotInstance = Bot()

# Handler for new users (persistent)
@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user
    if user is None:
        return

    # Check DB instead of in-memory set
    if db.logged_users.find_one({"user_id": user.id}):
        return  # Already logged

    # Insert user into DB
    db.logged_users.insert_one({"user_id": user.id, "username": user.username})

    # Log to your channel
    now = datetime.datetime.now(IST)
    text = (
        f"**#NewUser 👤**\n"
        f"- __@{bot.me.username}__\n\n"
        f"- **__User: {user.mention}__**\n"
        f"- **__User ID:__** `{user.id}`\n"
        f"- **__Date:__** __{now.strftime('%d-%b-%Y')}__\n"
        f"- **__Time:__** __{now.strftime('%I:%M %p')}__"
    )
    try:
        await bot.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"New user log failed: {e}")

BotInstance.run()
