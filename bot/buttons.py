from telethon import Button
import telethon
from bot.constants import SUPER_SUDO_USERNAME
from bot.db import C_GROUPS
from bot.exceptions import GroupNotExists


# Define three funciotns for creating buttons more easily
def button_text(text:str)->Button:
    """
    (SYNC)
    Create a button with text.

    :param text: str - The text to be displayed on the button.
    :return: telethon.tl.custom.button.Button
    """
    return Button.text(text,resize=True,single_use=True,selective=True)

def button_inline(text:str,data:str)->Button:
    """
    (SYNC)
    Create an inline button with text and data.

    :param text: str - The text to be displayed on the button.
    :param data: str - The data to be sent when the button is pressed.
    :return: telethon.tl.custom.button.Button
    """
    return Button.inline(text,data)

def button_url(text:str,url:str)->Button:
    """
    (SYNC)
    Create a button with text and url.

    :param text: str - The text to be displayed on the button.
    :param url: str - The url to be opened when the button is pressed.
    :return: telethon.tl.custom.button.Button
    """
    return Button.url(text,url)

# Contact to super admin
T_CONTACT_SUDO = "☎️  ارتباط با سودو " # Text
CONTACT_SUPER_ADMIN = [[button_url(T_CONTACT_SUDO,f"https://t.me/{SUPER_SUDO_USERNAME.replace('@','')}")]] # Buttons

# Configre admins in group
T_CONFIGURE_ADMINS = "پیکربندی" # Text
T_CLOSE_BTN = "بستن" # Text
CONFIGURE_ADMINS_BTN = [[button_inline(T_CONFIGURE_ADMINS,"configure_admins")],[button_inline(T_CLOSE_BTN,"close_sudo")]] # Buttons

# Panels

    # main panel
T_PANEL_HOME_11 = "تنظیمات قفل ها" # Text
T_PANEL_HOME_21 = "محدودیت کارکتر" # Text
T_BACK_HOME = "بازگشت به منوی اصلی"
T_CLOSE = "بستن منو"
def PANEL_HOME_BTN(user_id:int):
    """
    (SYNC)
    Create a button to open the panel.
    :param user_id: int - The user id who access the panel.
    """
    
    return [
        [button_inline(T_PANEL_HOME_11,f"{user_id}|group_locks")], #param1: how access to this button
        [button_inline(T_PANEL_HOME_21,f"{user_id}|char_limit")], #param1: how access to this button
    ]

    # locks panel
T_LOCK = "✅" # emoji
T_UNLOCK = "❌" # emoji
T_PANEL_LOCK = ["قفل عکس" # Text T_PANEL_LOCKS_11
,"قفل گیف" # Text T_PANEL_LOCKS_21
,"قفل فیلم" # Text T_PANEL_LOCKS_31
,"قفل ویدیو مسیج" # Text T_PANEL_LOCKS_51
,"قفل ویس" # Text T_PANEL_LOCKS_61
,"قفل استیکر" # Text T_PANEL_LOCKS_71
,"قفل فایل" # Text T_PANEL_LOCKS_81
,"قفل متن" # Text T_PANEL_LOCKS_91
,"قفل مخاطب" # Text T_PANEL_LOCKS_101
,"قفل موقعیت مکانی" # Text T_PANEL_LOCKS_111
,"قفل موسیقی" # Text T_PANEL_LOCKS_121
,"قفل نظرسنجی " # Text T_PANEL_LOCKS_131
,"قفل لینک دعوت" # Text T_PANEL_LOCKS_141
,"قفل لینک" # Text T_PANEL_LOCKS_151
,"قفل هشتگ"
,"قفل منشن"
,"قفل سرویس تلگرام" # Text T_PANEL_LOCKS_161
,"قفل فوروارد " # Text T_PANEL_LOCKS_171
,"قفل اینلاین " # Text T_PANEL_LOCKS_181
,"قفل دکمه شیشه ای" # Text T_PANEL_LOCKS_191
,"قفل همه " # Text T_PANEL_LOCKS_201
,"قفل کاربر بدون عکس پروفایل " # Text T_PANEL_LOCKS_201
]
def PANEL_LOCKS_BTN(chat_id:int,user_id):
    """
    (SYNC)
    Create a button to open the locks panel.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id who access the panel."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    locks = [[button_inline(text,""),button_inline(T_LOCK if lock_value else T_UNLOCK,f"{user_id}|{'unlock' if lock_value else 'lock'}=>{lock_name}")] for text,lock_name,lock_value in zip(T_PANEL_LOCK,group['locks'].keys(),group['locks'].values())]
    locks.append([button_inline(T_BACK_HOME,F"{user_id}|main_menu")])
    locks.append([button_inline(T_CLOSE,F"{user_id}|close_menu")])
    return locks
 

T_CHAR_LIMIT_1 = "وضعیت محدودیت کارکتر" # Text
T_CHAR_LIMIT_2 = "تعداد کارکتر" # Text
T_CHAR_LIMIT_3 = "جهت تنظیم عدد اینجا کلیک کنید" # Text
BACK_TO_CHAT_LIMIT_PANEL = lambda user_id: [button_inline("برگشت به پنل محدودیت کارکتر",f"{user_id}|char_limit")]
def PANEL_CHAR_LIMIT_BTN(chat_id:int,user_id:int):
    """
    (SYNC)
    Create a button to open the char limit panel.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id who access the panel."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    is_lock = T_LOCK if group['config']['char_limit']['enabled'] else T_UNLOCK
    limit = str(group['config']['char_limit']['limit'])
    return [
        [button_inline(T_CHAR_LIMIT_1,f""),button_inline(is_lock,f"{user_id}|toggleCharLimit")], #param1: how access to this button
        [button_inline(T_CHAR_LIMIT_2,f""),button_inline(limit,"")], #param1: how access to this button
        [button_inline(T_CHAR_LIMIT_3,f"{user_id}|setCharLimit")], #param1: how access to this button
        [button_inline(T_CLOSE,F"{user_id}|close_menu")]#param1: how access to this button
    ]

T_NEXTPAGE = "صفحه بعدی"
T_PREVIOUSPAGE = "صفحه قبلی"
def NEXTBACK_BTN(user_id:int,page:int,next:bool,prev:bool):
    """
    (SYNC)
    Create a button to open the char limit panel.
    
    :param user_id: int - The user id who access the panel.
    :param page: int - The page number."""
    btns = [[]]
    if next:
        btns[0].append(button_inline(T_NEXTPAGE,f"{user_id}|nextPageFilter=>{page+1}"))
    if prev:
        btns[0].append(button_inline(T_PREVIOUSPAGE,f"{user_id}|previousPageFilter=>{page-1}") if page>1 else button_inline(T_PREVIOUSPAGE,f""))
    if not(next or prev):
        return None
    return btns

async def mute_user(chat_id:int,user_id:int,time:int,client:telethon.TelegramClient):
    """
    (ASYNC)
    Mute a user in a group.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id to mute.
    :param time: int - The time to mute in seconds
    :param client: telethon.TelegramClient - The client to use."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    chat = await client.get_input_entity(chat_id)
    user = await client.get_input_entity(user_id)
    await client.edit_permissions(chat,user,0,send_messages=False)

async def unmute_user(chat_id:int,user_id:int,time:int,client:telethon.TelegramClient):
    """
    (ASYNC)
    Unmute a user in a group.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id to unmute.
    :param client: telethon.TelegramClient - The client to use."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    chat = await client.get_input_entity(chat_id)
    user = await client.get_input_entity(user_id)
    await client.edit_permissions(chat,user,0,send_messages=True)

async def ban_user(chat_id:int,user_id:int,time:int,client:telethon.TelegramClient):
    """
    (ASYNC)
    Ban a user in a group.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id to ban.
    :param client: telethon.TelegramClient - The client to use."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    chat = await client.get_input_entity(chat_id)
    user = await client.get_input_entity(user_id)
    await client.edit_permissions(chat,user,0,send_messages=False,view_messages=False)

async def unban_user(chat_id:int,user_id:int,time:int,client:telethon.TelegramClient):
    """
    (ASYNC)
    Unban a user in a group.
    
    :param chat_id: int - The chat id of group.
    :param user_id: int - The user id to unban.
    :param client: telethon.TelegramClient - The client to use."""
    group = C_GROUPS.find_one({"chat_id":chat_id})
    if not group:
        raise GroupNotExists("Group with chat_id {} not exists".format(chat_id))
    chat = await client.get_input_entity(chat_id)
    user = await client.get_input_entity(user_id)
    await client.edit_permissions(chat,user,0,send_messages=True,view_messages=True)