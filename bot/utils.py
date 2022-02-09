import logging
from typing import Coroutine, List

import telethon

from bot.constants import SUPER_SUDO_ID
from bot.db import C_GROUPS
from bot.exceptions import ClientAlreadyJoined, ClientNotJoined, GroupAlreadyExists, GroupNotExists, InvalidInviteLink


def get_admins(chat_id:int=[])->List[int]:
    """
    (SYNC)
    Get the list of admin IDs.
    :param chat_id: int - The chat ID to get the admins from.
    :return: List of admins
    """
    return [].append(SUPER_SUDO_ID)

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