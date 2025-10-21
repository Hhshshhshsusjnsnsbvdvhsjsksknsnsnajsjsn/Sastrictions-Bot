#Bot.py
import asyncio
import logging
import datetime
from datetime import timezone, timedelta
import aiohttp
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, KEEP_ALIVE_URL

# ✅ Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))

# Store logged users (in-memory)
LOGGED_USERS = set()


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


def find_all_plugins(*folders):
    """
    Recursively find all Python plugin files in the given folders.
    Returns a dict suitable for Pyrogram's plugins parameter.
    """
    plugins_dict = {}
    for root_dir in folders:
        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith(".py") and not file.startswith("__"):
                    rel_path = os.path.relpath(os.path.join(dirpath, file), root_dir)
                    module_name = rel_path.replace(os.sep, ".")[:-3]  # remove .py
                    plugins_dict[module_name] = os.path.join(dirpath, file)
    return plugins_dict


class Bot(Client):
    def __init__(self, plugin_folders=None):
        # Load all plugins recursively from given folders
        plugins_to_load = find_all_plugins(*plugin_folders) if plugin_folders else {}
        super().__init__(
            "Neon Login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=plugins_to_load,
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
            f"**- __@neonfiles__**"
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


# Pass the root folders of your repo here
BotInstance = Bot(plugin_folders=["Neon", "MyselfNeon"])

# Handler for new users (only logs once per user)
@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user
    if user is None:
        return

    # Log only if user not already logged
    if user.id not in LOGGED_USERS:
        LOGGED_USERS.add(user.id)

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
