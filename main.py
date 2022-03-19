# builin imports
from concurrent.futures import ProcessPoolExecutor
import os
import logging


# Initialize logging
logging.basicConfig(level=logging.INFO,filename="telethon.log",filemode="a+",format= '[%(levelname)s] {%(pathname)s:%(lineno)d} %(asctime)s %(message)s')    
logging.info("[!] Logging initialized")

# external imports
from telethon import events
import colorama

# package imports
from bot.constants import (BOT_TOKEN,PHONE_NUMBER)
from bot.utils import (get_admins)

from bot.clients import client,client_user
#Initialize colorama
colorama.init()
logging.info("[!] colorama initialized")







# Start the user client just for logging in
client_user.start(phone=PHONE_NUMBER)
logging.info("[!] User client started for logging in")
client_user.disconnect()
logging.info("[!] User client disconnected for logging in")

from bot.handlers import (handle_group_callback_admin, handle_group_message_admin, handle_group_message_user, handle_message,handle_admin_message)

# Add the event handler
client.add_event_handler(handle_message,events.NewMessage(func=lambda x: x.is_private and x.sender_id not in get_admins(x.chat_id)))
client.add_event_handler(handle_admin_message,events.NewMessage(func=lambda x: x.is_private and x.sender_id in get_admins(x.chat_id)))
client.add_event_handler(handle_group_message_admin,events.NewMessage(func=lambda x: not x.is_private and x.sender_id in get_admins(x.chat_id)))
client.add_event_handler(handle_group_message_user,events.NewMessage(func=lambda x: not x.is_private and x.sender_id not in get_admins(x.chat_id)))
client.add_event_handler(handle_group_callback_admin,events.CallbackQuery(func=lambda x: not x.is_private and x.sender_id in get_admins(x.chat_id)))

if __name__ == "__main__":
    try:
        # Connect to the Telegram server (API Bot)
        client.start(bot_token=BOT_TOKEN)
        logging.info("[!] Connected to Telegram server (API Bot)")

        # Connect to the Telegram server (User) in a separate process
        with ProcessPoolExecutor() as executor:
            client2_future = executor.submit(client_user.start,phone=PHONE_NUMBER)
            if not client2_future.done():
                logging.info("[!] Connected to Telegram server (User) in a separate process")
            else:
                logging.error("[!] Failed to connect to Telegram server (User) in a separate process")

                exit(1)


        os.system("clear" if os.name == "posix" else "cls")
        print(colorama.Fore.GREEN+"[!] Bot started"+colorama.Fore.RESET)
        # Run the client until you press Ctrl-C or the process receives SIGINT,
        client.run_until_disconnected()
    
    except KeyboardInterrupt:
        logging.info("[!] KeyboardInterrupt received")
    finally:
        client2_future.cancel()
        logging.info("[!] Canceled Telegram server (User) in a separate process")
        logging.info("[!] Exiting")
        os.system("clear" if os.name == "posix" else "cls")
        print(colorama.Fore.RED+"[!] Bot stoped"+colorama.Fore.RESET)
        exit(0)
