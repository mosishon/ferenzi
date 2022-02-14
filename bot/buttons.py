from telethon import Button
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
T_BACK_HOME = "بازگشت به منوی اصلی"
T_CLOSE = "بستن منو"
def PANEL_HOME_BTN(user_id:int):
    """
    (SYNC)
    Create a button to open the panel.
    :param user_id: int - The user id who access the panel.
    """
    
    return [
        [button_inline(T_PANEL_HOME_11,f"{user_id}|group_locks")] #param1: how access to this button
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
,"قفل سرویس تلگرام" # Text T_PANEL_LOCKS_161
,"قفل فوروارد " # Text T_PANEL_LOCKS_171
,"قفل اینلاین " # Text T_PANEL_LOCKS_181
,"قفل دکمه شیشه ای" # Text T_PANEL_LOCKS_191
,"قفل همه " # Text T_PANEL_LOCKS_201
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
 
