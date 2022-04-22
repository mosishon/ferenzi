import asyncio
import logging
import os
import telethon
from telethon.tl.custom import Message
from bot.constants import ANSWER_TYPES, BOT_ID, BOT_MESSAGE_DELTE_TIME, BOT_TOKEN, FILTER_TYPES, MINIMUM_CHAR_LIMIT, SUPER_SUDO_ID

from bot.db import C_FILTER, C_GROUPS
from bot.exceptions import GroupAlreadyExists, GroupNotExists
from bot.strings import (ADD_ANSWER, ADMIN_DEMOTE_SUCCESSFULLY, ADMIN_PROMOTE_SUCCESSFULLY, ANSEWR_TYPE_INVALID, ANSWER_ADDED, BAN_USER, BOT_ALREADY_INSTALLED,ADMINS_CONFIGURED, BOT_INSTALLED_SUCCESSFULLY, BOT_ISNOT_INSTALLED, BOT_UNINSTALLED_SUCCESSFULLY, CHAT_LIMIT_PANEL, CLEAR_ALL, CLEATING_FINISHED, CONFIGURE_ADMINS_COMMAND, DEMOTE, ENTER_CHAR_LIMIT, FILTER_ADDED, FILTER_TYPE_INVALID, FILTER_WORD, I_LEAVE_GROUP, IM_HERE_TO_HELP, LIST_FILTER, MAKE_ME_ADMIN, MUTE_USER, PANEL_TEXT, PANEL_TEXTS_TO_OPEN, PROMOTE, SHOULD_BE_GREATER_THAN_MINIMUM_CHAR_LIMIT, SHOULD_BE_NUMBER, SHOULD_REPLIED, START_ADMIN, START_SUDO_GROUP,START_USER, SUCCESFUL_CHAR_LIMIT_SET, THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU, UNBAN_USER, UNKNOWN_ERROR_OCURRED,BOT_CLI_TITLE,CONFIGURE_ADMINS, UNMUTE_USER)
from bot.buttons import (BACK_TO_CHAT_LIMIT_PANEL, CONTACT_SUPER_ADMIN,CONFIGURE_ADMINS_BTN, NEXTBACK_BTN, PANEL_CHAR_LIMIT_BTN, PANEL_HOME_BTN, PANEL_LOCKS_BTN, ban_user, mute_user, unban_user, unmute_user)
from bot.utils import add_answer, add_filter, add_new_admin, add_new_group, add_new_user, call_async, check_admin_access, check_answer, check_group, clear_all_message, configure_group_admins, delete_admin, delete_after, delete_group, get_admins, get_filter_list, get_media_type, get_mension, get_status, is_owner, is_sudo, join_group, leave_group, process_char_limit_delete, process_filter_delete, process_media_delete, process_profile_photo_delete, set_char_limit, set_status, toggle_char_limit, update_lock
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
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_group_message_admin")
    if not is_sudo(user_id):
        answer_ = await check_answer(chat_id,message,0)
        msg_id = answer_[1] if len(answer_)>1 else None
        media = None
        if msg_id:
            client_user_id = int(open("client_user_id","r").read())
            msg = await client.get_messages(client_user_id,ids=[int(msg_id)])
            media = msg[0].media
            await message.reply(answer_[0],link_preview=False,file=media)
            
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
                    if not os.path.exists("client_user_id"):
                        client_user_id = (await call_async(client_user,client_user.get_me)).id
                        open("client_user_id","w").write(str(client_user_id))
                    else:
                        client_user_id = int(open("client_user_id","r").read())
                    await client.edit_admin(chat,client_user_id,delete_messages=True,ban_users=True,title=BOT_CLI_TITLE)
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
            set_char_limit(chat_id,int(text))
            await message.respond(SUCCESFUL_CHAR_LIMIT_SET,buttons=PANEL_CHAR_LIMIT_BTN(chat_id,user_id))
            set_status(user_id,"")

    elif text.startswith(ADD_ANSWER):
        text = text.replace(ADD_ANSWER,"")
        reply = await message.get_reply_message()
        if not reply:
            return await message.respond(SHOULD_REPLIED)
        answer = reply.text
        media = reply.media
        media_id = None
        if media:
            await call_async(client_user,client_user.send_message,BOT_ID,"hi")
            if not os.path.exists("client_user_id"):
                client_user_id = (await call_async(client_user,client_user.get_me)).id
                print(client_user_id)
                open("client_user_id","w").write(str(client_user_id))
            else:
                client_user_id = int(open("client_user_id","r").read())
            msg = await reply.forward_to(client_user_id)
            media_id = msg.id
        answer_type = text.split(" ")[-1]
        word =  text.replace(answer_type,"").strip()
        ANSWER_TYPE = ANSWER_TYPES.get(answer_type.strip().lower())
        if ANSWER_TYPE is None:
            return await message.respond(ANSEWR_TYPE_INVALID)
        add_answer(chat_id,word,answer,ANSWER_TYPE,media_id)
        return await message.respond(ANSWER_ADDED.format(word,answer,answer_type))
    elif text.startswith(FILTER_WORD):
        text = text.replace(FILTER_WORD,"")
        filter_type_ = text.split()[0]
        filter_type = FILTER_TYPES.get(filter_type_.strip().lower())
        if not filter_type:
            return await message.reply(FILTER_TYPE_INVALID.format(filter_type_))
        text = text.replace(filter_type_,"").strip()
        if not text:
            return 
        add_filter(chat_id,text.strip,filter_type)
        await message.reply(FILTER_ADDED.format(text,filter_type_))
    elif text == LIST_FILTER:
        page1 = get_filter_list(chat_id,1)
        btns = NEXTBACK_BTN(user_id,1,page1[1]!=1,page1[2]!=1)
        if page1:
            await message.respond(page1[0],buttons=btns)
        else:
            await message.respond("empty")
     
    if await is_owner(user_id,chat_id,client):
        if text.lower() in CONFIGURE_ADMINS_COMMAND:
            count = await configure_group_admins(chat_id,client)
            await message.respond(ADMINS_CONFIGURED.format(count))
        elif text.lower() in DEMOTE:
            reply = await message.get_reply_message()
            if not reply:
                return await message.respond(SHOULD_REPLIED)
            repied_id = reply.sender_id
            delete_admin(chat_id,repied_id)
            
            await message.respond(ADMIN_DEMOTE_SUCCESSFULLY.format(get_mension(reply)),link_preview=False)
        elif text.lower() in PROMOTE:
            reply = await message.get_reply_message()
            if not reply:
                return await message.respond(SHOULD_REPLIED)
            repied_id = reply.sender_id
            add_new_admin(chat_id,repied_id)
            await message.respond(ADMIN_PROMOTE_SUCCESSFULLY.format(get_mension(reply)),link_preview=False)
    elif text.lower().startswith(BAN_USER):
        reply = await message.get_reply_message()
        user_idfb = None
        if reply:
            user_idfb = reply.sender_id
        else:
            user = text.replace(BAN_USER,"").strip()
            if user and ("@" in user):
                try:
                    user_idfb = (await client.get_input_entity(user))
                    if isinstance(user_id,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None
            elif user and user.isnumeric():
                try:
                    user_idfb = (await client.get_input_entity(int(user)))
                    if isinstance(user_idfb,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None

        if user_idfb:
            if user_idfb in get_admins(chat_id):
                return await message.respond("You can't ban admin!")
            await ban_user(chat_id,user_idfb,0,client)
        else:
            await message.respond("User Not Found!")
    elif text.lower().startswith(UNBAN_USER):
        reply = await message.get_reply_message()
        user_idfb = None
        if reply:
            user_idfb = reply.sender_id
        else:
            user = text.replace(UNBAN_USER,"").strip()
            if user and ("@" in user):
                try:
                    user_idfb = (await client.get_input_entity(user))
                    if isinstance(user_id,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None
            elif user and user.isnumeric():
                try:
                    user_idfb = (await client.get_input_entity(int(user)))
                    if isinstance(user_idfb,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None

        if user_idfb:
            if user_idfb in get_admins(chat_id):
                return await message.respond("You can't unban admin!")
            await unban_user(chat_id,user_idfb,0,client)
        else:
            await message.respond("User Not Found!")
    elif text.lower().startswith(MUTE_USER):
        reply = await message.get_reply_message()
        user_idfb = None
        if reply:
            user_idfb = reply.sender_id
        else:
            user = text.replace(MUTE_USER,"").strip()
            if user and ("@" in user):
                try:
                    user_idfb = (await client.get_input_entity(user))
                    if isinstance(user_id,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None
            elif user and user.isnumeric():
                try:
                    user_idfb = (await client.get_input_entity(int(user)))
                    if isinstance(user_idfb,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None

        if user_idfb:
            if user_idfb in get_admins(chat_id):
                return await message.respond("You can't mute admin!")
            await mute_user(chat_id,user_idfb,0,client)
        else:
            await message.respond("User Not Found!")
    elif text.lower().startswith(UNMUTE_USER):
        reply = await message.get_reply_message()
        user_idfb = None
        if reply:
            user_idfb = reply.sender_id
        else:
            user = text.replace(UNMUTE_USER,"").strip()
            if user and ("@" in user):
                try:
                    user_idfb = (await client.get_input_entity(user))
                    if isinstance(user_id,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None
            elif user and user.isnumeric():
                try:
                    user_idfb = (await client.get_input_entity(int(user)))
                    if isinstance(user_idfb,telethon.types.InputPeerUser):
                        user_idfb = user_idfb.user_id
                except ValueError:
                    user_idfb = None

        if user_idfb:
            if user_idfb in get_admins(chat_id):
                return await message.respond("You can't unmute admin!")
            await unmute_user(chat_id,user_idfb,0,client)
        else:
            await message.respond("User Not Found!")

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
    if access in (user_id,1) or is_sudo(user_id):

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
    add_new_user(user_id,chat_id)
    logging.debug(f"Received message: {text} from chat {chat_id} from user {user_id} on handle_group_message_user")
    if await process_media_delete(message):
        return
    elif await process_char_limit_delete(message):
        return
    elif await process_profile_photo_delete(message,client):
        return
    elif await process_filter_delete(message):
        return
    answer_ = await check_answer(chat_id,message,1)
    if len(answer_)>0:
        msg_id = answer_[1] if len(answer_)>1 else None
        media = None
        if msg_id:
            client_user_id = int(open("client_user_id","r").read())
            msg = await client.get_messages(client_user_id,ids=[int(msg_id)])
            media = msg[0].media
            

        await message.reply(answer_[0],link_preview=False,file=media)


async def chat_action_handler(message:telethon.events.ChatAction.Event):

    if await process_media_delete(message):
        return