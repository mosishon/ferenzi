import asyncio
import logging
from typing import Coroutine, List

import telethon
from telethon.tl.types import ChannelParticipantsAdmins

from bot.constants import SUPER_SUDO_ID,CLEARING_LIMIT
from bot.db import C_GROUPS, C_USERS
from bot.exceptions import ClientAlreadyJoined, ClientNotJoined, GroupAlreadyExists, GroupNotExists, InvalidInviteLink,UserAlreadyAdmin,InvalidLockName, UserAlreadyExists
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
    Check if a user is a SUPER sudo.

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
    :param owner: int - The owner ID to add.
    :return: None
    """
    # check if the group is already in the database
    if C_GROUPS.find_one({"chat_id":chat_id}):
        raise GroupAlreadyExists(f"Group {chat_id} already exists in the database.")
        
    return C_GROUPS.insert_one({
        "chat_id": chat_id,
        "admins":[],
        "config":{
            "char_limit":{
                "enabled":False,
                "limit":0,
            },
            "empty_profile":{
                "enabled":False,
                "limit":3,
                "action":"mute", #mute, kick, ban
            }

        },
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
            "all":False,
            "empty_profile":False,

        }
    })
    
def add_new_user(user_id:int,chat_id:int,if_not_exists:bool=True):
    """
    (SYNC)
    Add a new user to the database.

    :param user_id: int - The user ID to add.
    :param chat_id: int - The chat ID to add the user to.
    :param if_not_exists: bool - If the user not exists, create it. default: True.
    :return: None
    """
    # check if the user is already in the database
    user=C_USERS.find_one({"user_id":user_id})
    chat_warns  = {"profile_photo":{"count":0},"normal":{"count":0}}

    if not user:
        return C_USERS.update_one({"user_id":user_id},{"$set":{
            "warns":{
                str(chat_id):chat_warns
            },
        }},upsert=True)
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
    media_type = "all" if bool(group["locks"].get("all")) else media_type
    media_type = "forward" if message.forward else media_type
    media_type = "inline" if message.via_bot_id else media_type
    
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


def set_status(user_id:str,status:str):
    """
    (SYNC)
    Set the status of a user.
    :param user_id: str - The user ID to set.
    :param status: str - The status to set.
    :return: bool
    """
    return bool(C_USERS.update_one({"user_id":user_id},{"$set":{"status":status}},upsert=True))


def get_status(user_id:str):
    """
    (SYNC)
    Get the status of a user.
    :param user_id: str - The user ID to get.
    :return: str
    """
    user = C_USERS.find_one({"user_id":user_id})
    if not user:
        return ""
    return user.get("status","")


def set_char_limit(chat_id:int,limit:int):
    """
    (SYNC)
    Set the character limit for a group.
    :param chat_id: int - The chat ID to set.
    :param limit: int - The character limit to set.
    :return: bool
    """
    return bool(C_GROUPS.update_one({"chat_id":chat_id},{"$set":{"config.char_limit.limit":limit}}))

async def delete_after(message:telethon.custom.message.Message,time:int):
    """
    (ASYNC)
    Delete a message after a certain time.
    :param message: telethon.custom.message.Message - The message to delete.
    :param time: int - The time to wait before deleting the message.
    :return: None
    """
    await asyncio.sleep(time)
    await message.delete()

def toggle_char_limit(chat_id:int,):
    """
    (SYNC)
    Toggle the character limit for a group.
    :param chat_id: int - The chat ID to toggle.
    :return: bool
    """
    group = C_GROUPS.find_one({"chat_id":chat_id})
    enabled = not group["config"]["char_limit"]["enabled"]
    return bool(C_GROUPS.update_one({"chat_id":chat_id},{"$set":{"config.char_limit.enabled":enabled}}))

async def process_char_limit_delete(chat_id:int,message:telethon.tl.custom.Message):
    """
    (ASYNC)
    Delete a message if it exceeds the character limit.
    :param chat_id: int - The chat ID to check.
    :param message: telethon.tl.custom.Message - The message to check.
    :return: None
    """
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        return
    if group["config"]["char_limit"]["enabled"] and len(message.raw_text) > int(group["config"]["char_limit"]["limit"]):
        await message.delete()
        logging.debug(f"Deleted message {message.id} in group {chat_id} because it exceeded the character limit.")
        return True




def warn_profile_pic(user_id:int,chat_id:int):
    """
    (SYNC)
    Warn a user for changing their profile picture.
    :param user_id: int - The user ID to warn.
    :param chat_id: int - The chat ID to warn.
    :return: bool
    """
    return bool(C_USERS.update_one({"user_id":user_id},{"$inc":{f"warns.{chat_id}.profile_photo.count":1}}))

def clear_profile_warns(user_id:int,chat_id:int):
    """
    (SYNC)
    Clear the profile picture warning for a user.
    :param user_id: int - The user ID to clear.
    :param chat_id: int - The chat ID to clear.
    :return: bool
    """
    return bool(C_USERS.update_one({"user_id":user_id},{"$set":{f"warns.{chat_id}.profile_photo.count":0}}))
async def process_profile_photo_delete(chat_id:int,user_id:int,message:telethon.tl.custom.Message,client:telethon.TelegramClient):
    """
    (ASYNC)
    Delete a profile photo if it is empty.
    :param chat_id: int - The chat ID to check.
    :param user_id: int - The user ID to check.
    :param message: telethon.tl.custom.Message - The message to check.
    :param client: telethon.TelegramClient - The client to use.
    :return: None
    """
    group = C_GROUPS.find_one({"chat_id":chat_id})
    
    user = C_USERS.find_one({"user_id":user_id})
    groups_warn = user['warns'][str(chat_id)]
    if not group:
        return
    profs = await client.get_profile_photos(user_id,limit=1)
    if groups_warn['profile_photo']['count'] >=group['config']['empty_profile']['limit'] and len(profs)>0:
        clear_profile_warns(user_id,chat_id)
    if group["locks"]["empty_profile"] == True and len(profs)<1:
        await message.delete()
        if groups_warn['profile_photo']['count']>=group['config']['empty_profile']['limit']:
            logging.debug(f"Deleted msg {user_id} in group {chat_id} because the profile photo is empty.")
        else:
            await message.reply("WARN NO PROF PIC")
            warn_profile_pic(user_id,chat_id)
            logging.debug(f"Deleted msg and warn user {user_id} in group {chat_id} because the profile photo is empty.")
        return True


async def configure_group_admins(chat_id:int,client:telethon.TelegramClient):
    count = 0
    async for admin in client.iter_participants(chat_id,filter=ChannelParticipantsAdmins):
        count += 1
        if admin.id != SUPER_SUDO_ID:
            add_new_admin(chat_id,admin.id)
    return count    

async def is_owner(user_id:int,chat_id:int,client:telethon.TelegramClient):
    """
    (ASYNC)
    Check if a user is a group owner.
    :param user_id: int - The user ID to check.
    :param chat_id: int - The chat ID to check.
    :param client: telethon.TelegramClient - The client to use.
    :return: bool
    """
    owner = await client.get_participants(chat_id, filter=telethon.types.ChannelParticipantCreator)
    print(owner)
    return user_id == owner.id