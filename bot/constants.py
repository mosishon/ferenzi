import os
SESSION_NAME = 'API-SESSION'
SESSION2_NAME = 'USER-SESSION'
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_ID = int(BOT_TOKEN.split(":")[0])
PHONE_NUMBER = ''.strip()
DATABASE_NAME = 'ferenzi_bot' # lowercase name spaces and dot are not allowed use underscore instead ex: database_name

# Sudo details
SUPER_SUDO_USERNAME = "@MosiShon"
SUPER_SUDO_ID = 932528835


# Cli Bot
CLEARING_LIMIT = 10000 # how much messages to delete in a group

MINIMUM_CHAR_LIMIT = 50 # minimum characters to send a message
BOT_MESSAGE_DELTE_TIME = 5 # how much time to delete a message #TODO should be dynamic later


#ANSWER TYPES
ANSWER_TYPES = {
    "مدیر": 0,
    "کاربر": 1,
}

#FILTER TYPE
FILTER_TYPES = {
    "کلی":"0",
    "کلمه":'1'
}

#TZ
TIME_ZONE = "Asia/Tehran"
