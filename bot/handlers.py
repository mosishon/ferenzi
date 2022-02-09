import asyncio
import logging
from pickle import FALSE
import telethon
from telethon.tl.custom import Message
from bot.db import C_GROUPS
from bot.exceptions import GroupAlreadyExists, GroupNotExists
from bot.strings import (BOT_ALREADY_INSTALLED, BOT_INSTALLED_SUCCESSFULLY, BOT_ISNOT_INSTALLED, BOT_UNINSTALLED_SUCCESSFULLY, I_LEAVE_GROUP, IM_HERE_TO_HELP, MAKE_ME_ADMIN, START_ADMIN, START_SUDO_GROUP,START_USER, THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU, UNKNOWN_ERROR_OCURRED)
from bot.buttons import (CONTACT_SUPER_ADMIN)
from bot.utils import add_new_group, call_async, check_admin_access, delete_group, is_sudo, join_group, leave_group
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
                    add_new_group(chat_id)
                    await message.reply(BOT_INSTALLED_SUCCESSFULLY)
                    # get chat invite link
                    invite_link = await client(telethon.functions.messages.ExportChatInviteRequest(chat))
                    res = await join_group(client_user,invite_link.link)
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
        
        