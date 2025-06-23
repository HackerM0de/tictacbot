from client.client import Client
from client.database import DataBase
from dotenv import dotenv_values

TOKEN = dotenv_values()["TOKEN"]
try:
    GUILD_NAME = dotenv_values()["GUILD"]
except KeyError:
    GUILD_NAME = None
try:
    CHANNEL_NAME = dotenv_values()["CHANNEL"]
except KeyError:
    CHANNEL_NAME = None
try:
    MONGO_URI = dotenv_values()["MONGO_URI"]
    DB_NAME = dotenv_values()["DB_NAME"]
    database = DataBase(MONGO_URI, DB_NAME)
except KeyError:
    database = None
client = Client(guildName=GUILD_NAME, channelName=CHANNEL_NAME, db=database)
client.run(TOKEN)