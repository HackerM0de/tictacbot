from client.client import Client
from client.database import DataBase
from dotenv import dotenv_values

TOKEN = dotenv_values()["TOKEN"]
CHANNEL_NAME = dotenv_values()["CHANNEL"]
MONGO_URI = dotenv_values()["MONGO_URI"]
DB_NAME = dotenv_values()["DB_NAME"]
database = DataBase(MONGO_URI, DB_NAME)
client = Client(channelName=CHANNEL_NAME, db=database)
client.run(TOKEN)