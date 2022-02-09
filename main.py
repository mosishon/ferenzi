# builin imports
from concurrent.futures import ProcessPoolExecutor
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO,filename="telethon.log",filemode="a+",format= '[%(levelname)s] {%(pathname)s:%(lineno)d} %(asctime)s %(message)s')    
logging.info("[!] Logging initialized")

# external imports
from telethon import TelegramClient,events
import colorama

# package imports
from bot.constants import (BOT_TOKEN, SESSION_NAME,SESSION2_NAME,API_ID,API_HASH,PHONE_NUMBER)
from bot.handlers import (handle_message,handle_admin_message)
from bot.utils import (get_admins)
from bot.config import (PROXY)
from bot.db import (C_USERS,C_GROUPS,C_ADMINS)

#Initialize colorama
colorama.init()
logging.info("[!] colorama initialized")



# Create a TelegramClient instance (API Bot)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH,proxy=PROXY)

# Create a client instance (User)
client_user = TelegramClient(SESSION2_NAME, API_ID, API_HASH,proxy=PROXY)

# Add the event handler
client.add_event_handler(handle_message,events.NewMessage())
client.add_event_handler(handle_admin_message,events.NewMessage(from_users=get_admins()))

# Start the user client just for logging in
client_user.start(phone=PHONE_NUMBER)
logging.info("[!] User client started for logging in")
client_user.disconnect()
logging.info("[!] User client disconnected for logging in")

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
