import asyncio
import logging
import telethon
from telethon.tl.custom import Message
from bot.constants import BOT_MESSAGE_DELTE_TIME, MINIMUM_CHAR_LIMIT, SUPER_SUDO_ID

from bot.db import C_GROUPS
from bot.exceptions import GroupAlreadyExists, GroupNotExists
from bot.strings import (BOT_ALREADY_INSTALLED,ADMINS_CONFIGURED, BOT_INSTALLED_SUCCESSFULLY, BOT_ISNOT_INSTALLED, BOT_UNINSTALLED_SUCCESSFULLY, CHAT_LIMIT_PANEL, CLEAR_ALL, CLEATING_FINISHED, ENTER_CHAR_LIMIT, I_LEAVE_GROUP, IM_HERE_TO_HELP, MAKE_ME_ADMIN, PANEL_TEXT, PANEL_TEXTS_TO_OPEN, SHOULD_BE_GREATER_THAN_MINIMUM_CHAR_LIMIT, SHOULD_BE_NUMBER, START_ADMIN, START_SUDO_GROUP,START_USER, SUCCESFUL_CHAR_LIMIT_SET, THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU, UNKNOWN_ERROR_OCURRED,BOT_CLI_TITLE,CONFIGURE_ADMINS)
from bot.buttons import (BACK_TO_CHAT_LIMIT_PANEL, CONTACT_SUPER_ADMIN,CONFIGURE_ADMINS_BTN, PANEL_CHAR_LIMIT_BTN, PANEL_HOME_BTN, PANEL_LOCKS_BTN)
from bot.utils import add_new_admin, add_new_group, add_new_user, call_async, check_admin_access, check_group, clear_all_message, configure_group_admins, delete_after, delete_group, get_media_type, get_status, is_sudo, join_group, leave_group, process_char_limit_delete, process_media_delete, process_profile_photo_delete, set_char_limit, set_status, toggle_char_limit, update_lock
from bot.clients import client_user,client

async def handle_message(message:Message):
    """
    Handle a message from the user (NON-ADMINS).

    :param message: telethon.tl.custom.Message
    :return: None
    """
    text = message.text
    chat_id = message.chat_id
    user_id = message.sender_id
    chat = await message.get_input_chat()
    sender = await message.get_input_sender()
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_message")
    if text.lower() == "/start":
        await message.reply(START_USER,buttons=CONTACT_SUPER_ADMIN)


async def handle_admin_message(message:Message):
    """
    Handle a message from the admin (ADMINS).

    :param message: telethon.tl.custom.Message
    :return: None
    """
    text = message.text
    chat_id = message.chat_id
    user_id = message.sender_id
    chat = await message.get_input_chat()
    sender = await message.get_input_sender()
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_admin_message")
    if text.lower() == "/start":
        await message.reply(START_ADMIN)


async def handle_group_message_admin(message:Message):
    """
    Handle a message from admin or sudo in group.

    :param message: telethon.tl.custom.Message
    :return: None
    """
    text = message.text
    chat_id = message.chat_id
    user_id = message.sender_id
    chat = await message.get_input_chat()
    sender = await message.get_input_sender()
    status = get_status(user_id)
    access = 1
    args = []
    if "|" in status:
        access = int(status.split("|")[0])
        status = status.split("|")[1]
    if "=>" in status:
        args = status.split("=>")[1].split("-")
        status = status.split("=>")[0]
    print(args,status)
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_group_message_admin")
    if text.lower() in ("/start","نصب"):
        # Check if the user is a sudo or admin

        if is_sudo(user_id):
            await message.reply(START_SUDO_GROUP)

            try:
                # Add the group to the database if it's not there
                # check admin access
                is_admin = await check_admin_access(client,chat_id)
                if is_admin:
                    # get chat invite link
                    invite_link = await client(telethon.functions.messages.ExportChatInviteRequest(chat))
                    res = await join_group(client_user,invite_link.link)
                    client_user_id = await call_async(client_user,client_user.get_me)
                    await client.edit_admin(chat,client_user_id.id,delete_messages=True,ban_users=True,title=BOT_CLI_TITLE)
                    add_new_group(chat_id)
                    await message.reply(BOT_INSTALLED_SUCCESSFULLY)
                    await message.reply(CONFIGURE_ADMINS,buttons=CONFIGURE_ADMINS_BTN)


                    if res:
                        await call_async(client_user,client_user.send_message,chat_id,IM_HERE_TO_HELP)


                else:
                    await message.reply(MAKE_ME_ADMIN)
            except GroupAlreadyExists:
                # The group is already in the database
                await message.reply(BOT_ALREADY_INSTALLED)
            except:
                # Unknown error occurred
                await message.reply(UNKNOWN_ERROR_OCURRED)
                logging.exception(f"Error while installing bot in group {chat_id}")

        else:
            if text.lower() != "/start":
                await message.reply(THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU,buttons=CONTACT_SUPER_ADMIN)
        
    elif text.lower() in ("/stop","حذف نصب"):
        # Check if the user is a sudo or admin
        if is_sudo(user_id):
            try:
                # Remove the group from the database
                delete_group(chat_id,False)
                await message.reply(BOT_UNINSTALLED_SUCCESSFULLY)
                try:
                    await call_async(client_user,client_user.send_message,chat_id,I_LEAVE_GROUP)
                except (telethon.errors.ChannelPrivateError,telethon.errors.PeerIdInvalidError,ValueError):
                    pass
                await leave_group(client_user,chat_id)
                await leave_group(client,chat_id)
            except GroupNotExists:
                # The group is not in the database
                await message.reply(BOT_ISNOT_INSTALLED)
            except:
                # Unknown error occurred
                await message.reply(UNKNOWN_ERROR_OCURRED)
                logging.exception(f"Error while uninstalling bot in group {chat_id}")
        else:
            await message.reply(THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU,buttons=CONTACT_SUPER_ADMIN)
    elif text.lower() in PANEL_TEXTS_TO_OPEN:
        await message.reply(PANEL_TEXT,buttons=PANEL_HOME_BTN(user_id))
    elif text.lower() in CLEAR_ALL:
        task = asyncio.create_task(call_async(client_user,clear_all_message,client_user,chat_id))
        task.add_done_callback(lambda x: asyncio.create_task(call_async(client_user,client_user.send_message,chat_id,CLEATING_FINISHED)))
    elif status == "setCharLimit":
        if not text.isnumeric():
            await message.delete()
            m = await message.respond(SHOULD_BE_NUMBER)
            asyncio.create_task(delete_after(m,BOT_MESSAGE_DELTE_TIME))

        elif int(text) < MINIMUM_CHAR_LIMIT:
            await message.delete()
            m = await message.respond(SHOULD_BE_GREATER_THAN_MINIMUM_CHAR_LIMIT)
            asyncio.create_task(delete_after(m,BOT_MESSAGE_DELTE_TIME))

        else:
            await message.respond(SUCCESFUL_CHAR_LIMIT_SET,buttons=PANEL_CHAR_LIMIT_BTN(chat_id,user_id))
            set_char_limit(chat_id,int(text))
async def handle_group_callback_admin(message:telethon.events.CallbackQuery.Event):
    """
    Handle a callback from admin or sudo in group.

    :param message: telethon.tl.custom.Message
    :return: None
    """
    chat_id = message.chat_id
    if not check_group(chat_id):
        return
    user_id = message.sender_id
    chat = await message.get_input_chat()
    sender = await message.get_input_sender()
    access = 1
    args = []
    data = message.data.decode("utf8")
    logging.debug(f"Received callback: {data} from chat {chat_id} from user {user_id} on handle_group_callback_admin")
    if "|" in data:
        access = int(data.split("|")[0])
        data = data.split("|")[1]
    if "=>" in data:
        args = data.split("=>")[1].split("-")
        data = data.split("=>")[0]
    if data.lower() == "configure_admins":
        # Check if the user is a sudo or admin
        if is_sudo(user_id):
            count = await configure_group_admins(chat_id,client)
            await message.edit(ADMINS_CONFIGURED.format(count))
        else:
            await message.answer(THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU)
    elif data.lower() == "close_sudo" and is_sudo(user_id):
       await message.delete()

    # check if the admin access is enabled
    if access in (user_id,1) or user_id == SUPER_SUDO_ID:

        if data == "group_locks":
            await message.edit(f"locks of gp {chat_id} access for {access}",buttons=PANEL_LOCKS_BTN(chat_id,user_id))
        elif data == "lock":
            update_lock(chat_id,args[0],True)
            await message.edit(f"locks of gp {chat_id} access for {access}",buttons=PANEL_LOCKS_BTN(chat_id,user_id))
        elif data == "unlock":
            update_lock(chat_id,args[0],False)
            await message.edit(f"locks of gp {chat_id} access for {access}",buttons=PANEL_LOCKS_BTN(chat_id,user_id))
        elif data =="main_menu":
            await message.edit(PANEL_TEXT,buttons=PANEL_HOME_BTN(user_id))
        elif data =="close_menu":
            await message.delete()
        elif data == "char_limit":
            await message.edit(CHAT_LIMIT_PANEL,buttons=PANEL_CHAR_LIMIT_BTN(chat_id,user_id))
        elif data == "setCharLimit":
            await message.edit(ENTER_CHAR_LIMIT,buttons=BACK_TO_CHAT_LIMIT_PANEL(user_id))
            set_status(user_id,f"setCharLimit=>{chat_id}")
        elif data == "toggleCharLimit":
            toggle_char_limit(chat_id)
            await message.edit(CHAT_LIMIT_PANEL,buttons=PANEL_CHAR_LIMIT_BTN(chat_id,user_id))
    else:
        await message.answer(THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU)



async def handle_group_message_user(message:Message):
    """
    Handle a message from users in group.

    :param message: telethon.tl.custom.Message
    :return: None
    """
    chat_id = message.chat_id
    if not check_group(chat_id):
        return
    user_id = message.sender_id
    chat = await message.get_input_chat()
    sender = await message.get_input_sender()
    text = message.text
    media = message.media
    add_new_user(user_id,chat_id)
    print(message.via_bot)
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_group_message_user")
    if await process_media_delete(media,chat_id,message):
        return
    elif await process_char_limit_delete(chat_id,message):
        return
    elif await process_profile_photo_delete(chat_id,user_id,message,client):
        return
