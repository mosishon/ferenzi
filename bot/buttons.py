from telethon import Button
from bot.constants import SUPER_SUDO_USERNAME


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