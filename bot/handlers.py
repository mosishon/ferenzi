import logging
from telethon.tl.custom import Message
from bot.strings import (START_ADMIN,START_USER)
from bot.buttons import (CONTACT_SUPER_ADMIN)
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