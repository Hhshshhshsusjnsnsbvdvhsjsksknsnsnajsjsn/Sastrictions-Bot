# ---------------------------------------------------
# File Name: Start.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# YouTube: https://youtube.com/@MyselfNeon
# Created: 2025-10-21
# Last Modified: 2025-10-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import os
import asyncio
import random
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, VERIFY_TUTORIAL, START_PIC
from database.db import db
from MyselfNeon.strings import HELP_TXT
from MyselfNeon.verify import check_token, verify_user, check_verification, get_token

class batch_temp(object):
    IS_BATCH = {}

# --- Supported Telegram Reactions ---
REACTIONS = [
    "🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩",
    "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡",
    "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"
]

# --- Download status ---
async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"Downloaded: {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# --- Upload status ---
async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"Uploaded: {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# --- Progress writer ---
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Start command ---
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id, 
            message.from_user.first_name, 
            message.from_user.username
        )

    # ------------------------------------------
    # VERIFICATION CHECK FOR DEEP LINKS
    # ------------------------------------------
    if len(message.command) > 1:
        data = message.command[1]
        if data.split("-")[0] == "verify":
            try:
                _, user_id, token = data.split("-")
                user_id = int(user_id)
            except:
                return await message.reply("❌ Invalid Verification Link.")

            if message.from_user.id != user_id:
                return await message.reply("❌ This link is not for you!")

            if await check_token(user_id, token):
                await verify_user(client, user_id, token)
                return await message.reply("<b>✅ Verification Successful!</b>\n\nYou can now use the bot for 12 hours.")
            else:
                return await message.reply("<b>❌ Invalid or Expired Token!</b>\n\nUse /verify to get a new one.")
    # ------------------------------------------

    buttons = [
        [InlineKeyboardButton("Hᴏᴡ Tᴏ Usᴇ Mᴇ 🤔", callback_data="help_btn")],
        [
            InlineKeyboardButton('Uᴘᴅᴀᴛᴇ 🔥', url='https://t.me/NeonFiles'),
            InlineKeyboardButton('Aʙᴏᴜᴛ 😎', callback_data="about_btn")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Define the text separately to use in both photo caption or text message
    start_text = (
        f"<blockquote>**__Yoo !! {message.from_user.mention}__ 😇**</blockquote>\n"
        "<blockquote>**__I’m Save Restricted Content Bot. I Can Help You Unlock And Save Restricted Posts From Telegram By Their Links.__**\n\n"
        "**__🔑 Please /login First — This Is Required For Downloading Content.__**</blockquote>\n"
    )

    # Check if START_PIC is available
    if START_PIC:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=START_PIC,
            caption=start_text,
            reply_markup=reply_markup,
            reply_to_message_id=message.id
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text=start_text,
            reply_markup=reply_markup,
            reply_to_message_id=message.id
        )

    try:
        await message.react(
            emoji=random.choice(REACTIONS),
            big=True
        )
    except Exception as e:
        print(f"Reaction failed: {e}")

# -------------------
# Help command (standalone)
# -------------------
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )

# -------------------
# Cancel command
# -------------------
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="❌ Batch Successfully Cancelled.",
        quote=True
    )

# -------------------
# Handle incoming messages
# -------------------
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # ------------------------------------------
    # VERIFICATION CHECK BEFORE PROCESSING
    # ------------------------------------------
    if not await check_verification(message.from_user.id):
        btn = [[InlineKeyboardButton("Verify Now", callback_data="verify_query")]]
        return await message.reply_text(
            "❌ <b>You are not verified!</b>\n\nPlease verify your account to download files.",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    # ------------------------------------------

    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text(
                "One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel"
            )

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**__For Downloading Restricted Content You Have To /login First.__**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return

            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**__Your Login Session Expired. So /logout First Then Login Again By - /login__**")

            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(message.chat.id, "**__The username is not occupied by anyone.__**",
                                              reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(3)

        batch_temp.IS_BATCH[message.from_user.id] = True

# -------------------
# Handle private content
# -------------------
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if "Text" == msg_type:
        try:
            await client.send_message(chat, f"**__{msg.text}__**", entities=msg.entities, reply_to_message_id=message.id,
                                      parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id,
                                          parse_mode=enums.ParseMode.HTML)
            return

    smsg = await client.send_message(message.chat.id, '**__Downloading 🚀__**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id,
                                      parse_mode=enums.ParseMode.HTML)
        return await smsg.delete()

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    caption = msg.caption if msg.caption else None
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    try:
        if "Document" == msg_type:
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id,
                                       parse_mode=enums.ParseMode.HTML, progress=progress,
                                       progress_args=[message, "up"])
            if ph_path: os.remove(ph_path)

        elif "Video" == msg_type:
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width,
                                    height=msg.video.height, thumb=ph_path, caption=caption,
                                    reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                    progress=progress, progress_args=[message, "up"])
            if ph_path: os.remove(ph_path)

        elif "Animation" == msg_type:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif "Sticker" == msg_type:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif "Voice" == msg_type:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities,
                                    reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                    progress=progress, progress_args=[message, "up"])

        elif "Audio" == msg_type:
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id,
                                    parse_mode=enums.ParseMode.HTML, progress=progress,
                                    progress_args=[message, "up"])
            if ph_path: os.remove(ph_path)

        elif "Photo" == msg_type:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id,
                                    parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id,
                                      parse_mode=enums.ParseMode.HTML)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)

    await client.delete_messages(message.chat.id, [smsg.id])

#-------------------
# Get message type
# -------------------
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass
    try:
        msg.video.file_id
        return "Video"
    except:
        pass
    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass
    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass
    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass
    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass
    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass
    try:
        msg.text
        return "Text"
    except:
        pass

# --- Inline button callback ---
@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query):
    data = callback_query.data
    message = callback_query.message

    # --- NEW VERIFY BUTTON HANDLE ---
    if data == "verify_query":
        # Acknowledge the callback immediately to stop the spinning
        await callback_query.answer("Generating link...", show_alert=False)
        
        bot_info = await client.get_me()
        start_link = f"https://t.me/{bot_info.username}?start="
        
        try:
            # Generate the token and short link
            verify_url = await get_token(client, callback_query.from_user.id, start_link)
            
            buttons = [
                [InlineKeyboardButton("🔗 Click Here To Verify", url=verify_url)],
                [InlineKeyboardButton("❓ How To Verify", url=VERIFY_TUTORIAL)]
            ]
            
            await client.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.id,
                text="<b><i>🔐 Verification Required !</i></b>\n\n"
                     "<i>To continue using this Bot, you must Verify your Account.</i>\n"
                     "<i>The Token is valid for 12 Hours.</i>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error generating link: {e}")

    # Help button  
    elif data == "help_btn":
        help_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_btn"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start_btn")
            ]
        ])
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=HELP_TXT,
            reply_markup=help_buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await callback_query.answer()

    # About button
    elif data == "about_btn":
        me = await client.get_me()
        about_text = (
            "<b><blockquote>‣ 📝 𝐌𝐘 𝐃𝐄𝐓𝐀𝐈𝐋𝐒</blockquote>\n\n"
            "<i>• Mʏ Nᴀᴍᴇ : <a href='https://t.me/SaveRestriction_oBot'>Save Restrictions</a>\n"
            "• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ : <a href='tg://settings'>Tʜɪs Sᴡᴇᴇᴛɪᴇ ❤️</a>\n"
            "• Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/MyselfNeon'>@MʏsᴇʟғNᴇᴏɴ</a>\n"
            "• Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>\n"
            "• Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>Pʏᴛʜᴏɴ 𝟹</a>\n"
            "• DᴀᴛᴀBᴀsᴇ : <a href='https://www.mongodb.com/'>Mᴏɴɢᴏ DB</a>\n"
            "• Bᴏᴛ Sᴇʀᴠᴇʀ : <a href='https://heroku.com'>Hᴇʀᴏᴋᴜ</a>\n"
            "• Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.𝟽 [Sᴛᴀʙʟᴇ]</i></b>"
        )

        about_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ 🔊", url="https://t.me/+o1s-8MppL2syYTI9"),
                InlineKeyboardButton("Sᴏᴜʀᴄᴇ Cᴏᴅᴇ 💡", url="https://myselfneon.github.io/neon/")
            ],
            [
                InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_btn"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start_btn")
            ]
        ])

        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=about_text,
            reply_markup=about_buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await callback_query.answer()

    # --- Home / Start button ---
    elif data == "start_btn":
        start_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Hᴏᴡ Tᴏ Usᴇ Mᴇ 🤔", callback_data="help_btn")],
            [
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇ 🔥", url="https://t.me/NeonFiles"),
                InlineKeyboardButton("Aʙᴏᴜᴛ 😎", callback_data="about_btn")
            ]
        ])
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=(
                f"<blockquote>**__Yoo !! {callback_query.from_user.mention}__ 👋**</blockquote>\n"
                "<blockquote>**__I’m Save Restricted Content Bot. I Can Help You Unlock And Save Restricted Posts From Telegram By Their Links.__**\n\n"
                "**__🔑 Please /login First — This Is Required For Downloading Content.__**</blockquote>\n"
            ),
            reply_markup=start_buttons
        )
        await callback_query.answer()

    # --- Close button ---
    elif data == "close_btn":
        await client.delete_messages(message.chat.id, [message.id])
        await callback_query.answer()


# Don't remove Credits
# Developer Telegram @MyselfNeon
# Update channel - @NeonFiles
