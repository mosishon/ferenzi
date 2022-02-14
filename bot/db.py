from pymongo import MongoClient,database
from bot.constants import (DATABASE_NAME)
import logging
# Connect to the database
try:
    client = MongoClient('localhost', 27017)
    logging.info("[!] Connected to MongoDB")
except:
    logging.error("[!] Failed to connect to MongoDB")
    exit(1)
db:database.Database = getattr(client, DATABASE_NAME)
# Get the collection
C_USERS = db.users
C_GROUPS = db.groups

