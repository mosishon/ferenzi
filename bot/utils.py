import logging
from typing import Coroutine, List

import telethon

from bot.constants import SUPER_SUDO_ID,CLEARING_LIMIT
from bot.db import C_GROUPS
from bot.exceptions import ClientAlreadyJoined, ClientNotJoined, GroupAlreadyExists, GroupNotExists, InvalidInviteLink,UserAlreadyAdmin,InvalidLockName
from bot.strings import CLEARING_STARTED

def get_admins(chat_id:int)->List[int]:
    """
    (SYNC)
    Get the list of admin IDs.
    :param chat_id: int - The chat ID to get the admins from.
    [!] raise bot.exceptions.GroupNotExists if the group doesn't exist in the database.
    :return: List of admins
    """
    group = C_GROUPS.find_one({"chat_id":chat_id})or {}
    # if not group:
    #     raise GroupNotExists(f"Group {chat_id} does not exist in the database.")
    logging.debug(f"Group {chat_id} admins: {group.get('admins')}")
    return group.get('admins',[])+[SUPER_SUDO_ID]

def is_sudo(user_id:int)->bool:
    """
    (SYNC)
    Check if a user is a sudo.

    :param user_id: int - The user ID to check.
    :return: bool
    """
    return user_id == SUPER_SUDO_ID

def normalize_invite_link(invite_link:str)->str:
    """
    (SYNC)
    Normalize an invite link.

    :param invite_link: str - The invite link to normalize.
    :return: str
    """
    return invite_link.split("/")[-1].replace("+","")

def add_new_group(chat_id:int):
    """
    (SYNC)
    Add a new group to the database.

    :param chat_id: int - The chat ID to add.
    :return: None
    """
    # check if the group is already in the database
    if C_GROUPS.find_one({"chat_id":chat_id}):
        raise GroupAlreadyExists(f"Group {chat_id} already exists in the database.")
        
    return C_GROUPS.insert_one({
        "chat_id": chat_id,
        "admins":[],
        "locks":{
            "photo":False,
            "gif":False,
            "video":False,
            "video_note":False,
            "voice":False,
            "sticker":False,
            "document":False,
            "text":False,
            "contact":False,
            "location":False,
            "audio":False,
            "poll":False,
            "invite_link":False,
            "link":False,
            "telegram_service":False,
            "forward":False,
            "inline":False,
            "inline_button":False,
            "all":False

        }
    })
    
def delete_group(chat_id:int,if_exists:bool=True):
    """
    (SYNC)
    Delete a group from the database.

    :param chat_id: int - The chat ID to delete.
    :param if_exists: bool - If the group exists, delete it. default: True.
    [!] raise bot.exceptions.GroupNotExists if the group doesn't exist in the database and if_exists is False.
    :return: None
    """
    if not if_exists and not C_GROUPS.find_one({"chat_id":chat_id}):
        raise GroupNotExists(f"Group {chat_id} does not exist in the database.")
    return C_GROUPS.delete_one({"chat_id":chat_id})

async def leave_group(client:telethon.TelegramClient,chat_id:int,if_joined:bool=False):
    """
    (ASYNC)
    Leave a group.

    :param client: telethon.TelegramClient - The client to use.
    :param chat_id: int - The chat ID to leave.
    :param if_joined: bool - leave if client is already joined. default: False.
    [!] raise bot.exceptions.ClientNotJoined if the client is not joined to the group. and if_joined is False.
    :return: None
    """
    try:
        connected_now=False
        if not client.is_connected():
            connected_now=True

            await client.connect()
        await client(telethon.functions.channels.LeaveChannelRequest(chat_id))
    except: #TODO: check if the client was not joined to the group
        if if_joined:
            raise ClientNotJoined(f"Client is not joined to group {chat_id}.")
    finally:
        if connected_now:
            await client.disconnect()
async def join_group(client:telethon.TelegramClient,invite_link:str,if_not_joined:bool=False):
    """
    (ASYNC)
    Join a group.

    :param client: telethon.TelegramClient - The client to use.
    :param invite_link: str - The invite link to join.with https://t.me/joinchat/ for private groups. and with @ for public groups.
    :param if_not_joined: bool - join if client is not already joined. default: False.
    [!] raise bot.exceptions.ClientAlreadyJoined if the client is already joined to the group. and if_not_joined is False.
    [!] raise bot.exceptions.InvalidInviteLink if the invite link is invalid.
    :return: None
    """
    if "https" in invite_link:
        GROUP_TYPE="private"
    elif "@" in invite_link:
        GROUP_TYPE="public"
    else:
        raise InvalidInviteLink(f"Invalid invite link {invite_link}.")
    try:
        if not client.is_connected():
            connected_now=True
            await client.connect()
        if GROUP_TYPE=="private":
            logging.info(f"Joining group {invite_link.split('/')[-1]}")
            await client(telethon.functions.messages.ImportChatInviteRequest(normalize_invite_link(invite_link)))
        elif GROUP_TYPE=="public":
            await client(telethon.functions.channels.JoinChannelRequest(invite_link))
    except telethon.errors.UserAlreadyParticipantError:
        if if_not_joined:
            raise ClientAlreadyJoined(f"Client is already joined to group {invite_link}.")
        if connected_now:
            await client.disconnect()

    
        
async def check_admin_access(client:telethon.TelegramClient,chat_id:int):
    """
    (ASYNC)
    Check if the client has admin access to the group.

    :param client: telethon.TelegramClient - The client to use.
    :param chat_id: int - The chat ID to check.
    :return: bool
    """
    try:
        connected_now=False
        if not client.is_connected():
            connected_now=True
            await client.connect()
        admin_rights = await client.get_permissions(chat_id,await client.get_me())
        
        return admin_rights.change_info and admin_rights.delete_messages and admin_rights.invite_users and admin_rights.pin_messages and admin_rights.add_admins 
    finally:
        if connected_now:
            await client.disconnect()

    
async def call_async(client:telethon.TelegramClient,func:Coroutine,*args,**kwargs):
    """
    (ASYNC)
    Call a function asynchronously.

    :param client: telethon.TelegramClient - The client to use.
    :param func: Coroutine - The function to call.
    :return: function result
    """
    try:
        connected_now=False

        if not client.is_connected():
            await client.connect()
            connected_now=True

        return await func(*args,**kwargs)
    finally:
        if connected_now:
            await client.disconnect()
        
def add_new_admin(chat_id:int,user_id:int,if_not_exists:bool=True):
    """
    (SYNC)
    Add a new admin to the database.

    :param chat_id: int - The chat ID to add.
    :param user_id: int - The user ID to add.
    :param if_not_exists: bool - If the admin exists, add it. default: True.
    [!] raise bot.exceptions.UserAlreadyAdmin. if the user is already an admin. and if_not_exists is False.
    :return: None
    """
    # check if the group exists
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists(f"Group {chat_id} does not exist in the database.")
    
    # check if the user exists in group admins
    if int(user_id) in group["admins"]:
        # if the user is already an admin, and if_not_exists is False, raise an exception
        if not if_not_exists:
            raise UserAlreadyAdmin(f"User {user_id} is already an admin of group {chat_id}.")
        else:
            return
    return C_GROUPS.update_one({"chat_id":chat_id},{"$push":{"admins":int(user_id)}}) 

def update_lock(chat_id:int,lock_name:str,lock_value:bool):
    """
    (SYNC)
    Update the lock of the group.
    :param chat_id: int - The chat ID to update.
    :param lock_name: str - The lock name to update.
    :param lock_value: bool - The lock value to update.
    :return: None
    [!] raise bot.exceptions.GroupNotExists if the group does not exist.
    [!] raise bot.exceptions.InvalidLockName if the lock name is invalid.
    """
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists(f"Group {chat_id} does not exist in the database.")
    if lock_name not in group["locks"]:
        raise InvalidLockName(f"Invalid lock name {lock_name}.")
    return C_GROUPS.update_one({"chat_id":chat_id},{"$set":{"locks."+lock_name:lock_value}})

def get_media_type(media:telethon.tl.types.MessageMediaDocument):
    """
    (SYNC)
    Get the media type of a message.

    :param media: telethon.tl.types.MessageMedia - The media to check.
    :return: str - The media type.
    """
    if isinstance(media,telethon.tl.types.MessageMediaPhoto):
        return "photo"
    elif isinstance(media,telethon.tl.types.MessageMediaDocument):
        if media.document.mime_type.startswith("image/"):
            if media.document.mime_type.split("/")[-1] == "webp":
                return "sticker"
            return "photo"
        elif media.document.mime_type.startswith("video/"):
            if isinstance(media.document.attributes[-1],telethon.tl.types.DocumentAttributeAnimated):
                return "gif"
            return "video"
        elif media.document.mime_type.startswith("audio/"):
            if media.document.mime_type.split("/")[-1] == "ogg":
                return "voice"
            return "audio"
        elif media.document.mime_type.startswith("application/"):
            if media.document.mime_type.split("/")[-1] == "x-tgsticker":
                return "sticker"
        return "document"
    elif isinstance(media,telethon.tl.types.MessageMediaContact):
        return "contact"
    elif isinstance(media,telethon.tl.types.MessageMediaGeo):
        return "geo"
    elif isinstance(media,telethon.tl.types.MessageMediaVenue):
        return "venue"
    elif isinstance(media,telethon.tl.types.MessageMediaGeoLive):
        return "location"
    elif isinstance(media,telethon.tl.types.MessageMediaGame):
        return "game"
    elif isinstance(media,telethon.tl.types.MessageMediaInvoice):
        return "invoice"
    elif isinstance(media,telethon.tl.types.MessageMediaUnsupported):
        return "unsupported"
    elif isinstance(media,telethon.tl.types.MessageMediaWebPage):
        return "web_page"
    elif isinstance(media,telethon.tl.types.MessageMediaPoll):
        return "poll"
    elif isinstance(media,telethon.tl.types.MessageMediaDice):
        return "dice"
    elif isinstance(media,telethon.tl.types.MessageMediaGame):
        return "game"
    elif isinstance(media,telethon.tl.types.MessageMediaInvoice):
        return "invoice"
    else:
        return "unknown"

async def process_media_delete(media:telethon.tl.types.MessageMediaDocument,chat_id:int,message:telethon.tl.custom.Message):
    """
    process media and locks, and delete message if needed.
    :param media: telethon.tl.types.MessageMedia - The media to check.
    :param chat_id: int - The chat ID to check.
    :param message: telethon.tl.custom.Message - The message to check.
    [!] raise bot.exceptions.GroupNotExists if the group does not exist.
    :return: None
    """
    # check if the group exists
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists(f"Group {chat_id} does not exist in the database.")
    
    # check if the media type is locked
    media_type = get_media_type(media)
    if group["locks"].get(media_type) == True:
        await message.delete()
        logging.debug(f"Deleted message {message.id} in group {chat_id} because the media type ({media_type}) is locked.")
        return True
    return False

async def clear_all_message(client:telethon.TelegramClient,chat_id:int):
    print("Start clearing")
    """
    (ASYNC)
    Clear all messages in a group.
    :param client: telethon.TelegramClient - The client to use.
    :param chat_id: int - The chat ID to clear.
    [!] raise bot.exceptions.GroupNotExists if the group does not exist.
    :return: None
    """
    # check if the group exists
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists(f"Group {chat_id} does not exist in the database.")

    # alert the user, process started    
    msg = await client.send_message(chat_id,CLEARING_STARTED)
    await client.delete_messages(chat_id,list(range(msg.id-CLEARING_LIMIT,msg.id)),revoke=True)

def check_group(chat_id:int):
    """
    (SYNC)
    Check if the group exists.
    :param chat_id: int - The chat ID to check.
    :return: bool - True if the group exists, False otherwise.
    """
    return bool(C_GROUPS.find_one({"chat_id":chat_id}))